from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
import re

from .models import User, Listing, CreateListing, PlaceBid, Bid, Comment, Watchlist, CommentForm


def index(request):

    try:
        checkBid = Bid.objects.filter(
            placedTo=Listing.objects.get(title=title)).order_by('-id')[0]
        currentBid = re.findall("bid:(.+) on:", str(checkBid))[0]
    except:
        currentBid = 0

    getWatchlist = ""
    if request.user.is_authenticated:
        # Watchlist
        current_user = request.user
        getWatchlist = Watchlist.objects.filter(user=f'{ current_user.id }')

    lm = []
    ls = Listing.objects.all()
    for listing in ls:
        try:
            checkBid = Bid.objects.filter(
                placedTo=Listing.objects.get(title=listing.title)).order_by('-id')[0]
            currentBid = checkBid.amount
        except:
            currentBid = 0

        if float(listing.startingBid) <= float(currentBid):
            bid = currentBid
        else:
            bid = listing.startingBid

        la = {
            "title": listing.title,
            "description": listing.description,
            "bid": bid,
            "imageURL": listing.imageURL,
            "category": listing.category
        }
        lm.append(la)

    return render(request, "auctions/index.html", {
        "listings": lm,
        "watchlistLen": len(getWatchlist)
    })


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("commerce:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("commerce:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("commerce:index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == "POST":
        current_user = request.user
        title = request.POST["title"]
        description = request.POST["description"]
        startingBid = str(format(float(request.POST["startingBid"]), '.2f'))
        imageURL = request.POST["imageURL"]
        if imageURL == "":
            imageURL = "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcRJQ9xu5I_En7x6FYaQ8Mlf2QSMCg1cFAUu7w&usqp=CAU"
        category = request.POST["category"]
        ls = Listing(title=title, description=description,
                     startingBid=startingBid, imageURL=imageURL, category=category, user=request.user, status="opened")
        ls.save()

    current_user = request.user
    # Watchlist
    getWatchlist = Watchlist.objects.filter(user=f'{ current_user.id }')
    watchlistLen = len(getWatchlist)

    return render(request, "auctions/create_listing.html", {
        "createListing": CreateListing,
        "watchlistLen": watchlistLen
    })


def listing(request, listingTitle):
    if request.method == "POST":
        if request.user.is_authenticated:
            current_user = request.user
            print(request.POST)

            # Get type of action
            try:
                action = request.POST["action"]
            except:
                action = None

            if action == "close_auction":
                getListing = Listing.objects.get(
                    title=request.POST["listingTitle"])
                getListing.status = "closed"
                getListing.save()

            if action == "comment":
                comment = Comment(
                    title=request.POST["title"], comment=request.POST["comment"], commentBy=User.objects.get(username=request.POST["commentBy"]))
                comment.save()

            if action == "bid":
                currentBid = request.POST["currentBid"]
                bidPlaced = request.POST["bid"]
                if float(bidPlaced) >= float(currentBid):
                    message = "Your bid was secussefully set!"
                    listing = request.POST["placedTo"]
                    updateBid = Bid(placedBy=User.objects.get(id=current_user.id), placedTo=Listing.objects.get(
                        title=listing), amount=bidPlaced)
                    updateBid.save()

                    getWatchlist = ""
                    onWatchlist = 0
                    getObject = Listing.objects.filter(
                        title=f'{ listingTitle }')

                    # Look if there is was a bid so far
                    startingBid = getObject[0].startingBid
                    try:
                        checkBid = Bid.objects.filter(
                            placedTo=Listing.objects.get(title=getObject[0].title)).order_by('-id')[0]
                        currentBid = re.findall(
                            "bid:(.+) on:", str(checkBid))[0]
                    except:
                        currentBid = 0

                    if float(startingBid) <= float(currentBid):
                        bid = currentBid
                    else:
                        bid = startingBid

                    listingDetails = {
                        "title": getObject[0].title,
                        "description": getObject[0].description,
                        "bid": bid,
                        "imageURL": getObject[0].imageURL,
                        "category": getObject[0].category
                    }

                    if request.user.is_authenticated:
                        current_user = request.user
                        # Check if user got a watchlist
                        getWatchlist = Watchlist.objects.filter(
                            user=f'{ current_user.id }')
                        onWatchlist = 0

                        for entry in getWatchlist:
                            found = re.search(
                                f"title:{ getObject[0].title }", str(entry))
                            if found:
                                onWatchlist = 1
                                break

                    return render(request, "auctions/listing.html", {
                        "listing": listingDetails,
                        "placeBid": PlaceBid,
                        "watchlist": onWatchlist,
                        "watchlistLen": len(getWatchlist),
                        "status": "success",
                        "message": message
                    })
                else:
                    getWatchlist = ""
                    onWatchlist = 0
                    getObject = Listing.objects.filter(
                        title=f'{ listingTitle }')

                    # Look if there is was a bid so far
                    startingBid = getObject[0].startingBid
                    try:
                        checkBid = Bid.objects.filter(
                            placedTo=Listing.objects.get(title=getObject[0].title)).order_by('-id')[0]
                        currentBid = re.findall(
                            "bid:(.+) on:", str(checkBid))[0]
                    except:
                        currentBid = 0

                    if float(startingBid) <= float(currentBid):
                        bid = currentBid
                    else:
                        bid = startingBid

                    listingDetails = {
                        "title": getObject[0].title,
                        "description": getObject[0].description,
                        "bid": bid,
                        "imageURL": getObject[0].imageURL,
                        "category": getObject[0].category
                    }
                    message = "Your bid was lower than the current price"

                    if request.user.is_authenticated:
                        current_user = request.user
                        # Check if user got a watchlist
                        getWatchlist = Watchlist.objects.filter(
                            user=f'{ current_user.id }')
                        onWatchlist = 0

                        for entry in getWatchlist:
                            found = re.search(
                                f"title:{ getObject[0].title }", str(entry))
                            if found:
                                onWatchlist = 1
                                break

                    return render(request, "auctions/listing.html", {
                        "listing": listingDetails,
                        "placeBid": PlaceBid,
                        "watchlist": onWatchlist,
                        "watchlistLen": len(getWatchlist),
                        "status": "error",
                        "message": message
                    })

            # if action is related to watchlist actions
            if action == "watchlist_add" or action == "watchlist_remove":
                watchlistItem = request.POST["watchlistItem"]
                if action == "watchlist_add":
                    watchlistUpdate = Watchlist(
                        user=User.objects.get(id=current_user.id), listing=Listing.objects.get(
                            title=watchlistItem))
                    watchlistUpdate.save()

                if action == "watchlist_remove":
                    watchlistUpdate = Watchlist.objects.get(
                        user=current_user, listing=Listing.objects.get(title=watchlistItem))
                    watchlistUpdate.delete()

    # Listing Information
    getWatchlist = ""
    onWatchlist = 0
    getObject = Listing.objects.filter(title=f'{ listingTitle }')

    # Look if there is was a bid so far
    startingBid = getObject[0].startingBid
    try:
        checkBid = Bid.objects.filter(
            placedTo=Listing.objects.get(title=getObject[0].title)).order_by('-id')[0]
        currentBid = re.findall("bid:(.+) on:", str(checkBid))[0]
        print(checkBid)
    except:
        currentBid = 0

    if float(startingBid) <= float(currentBid):
        bid = currentBid
    else:
        bid = startingBid

    listingDetails = {
        "title": getObject[0].title,
        "description": getObject[0].description,
        "bid": bid,
        "imageURL": getObject[0].imageURL,
        "category": getObject[0].category,
        "createdBy": getObject[0].user,
        "status": getObject[0].status
    }

    message = ""
    highestBidder = None

    if request.user.is_authenticated:
        current_user = request.user
        # Check if user got a watchlist
        getWatchlist = Watchlist.objects.filter(user=f'{ current_user.id }')
        onWatchlist = 0

        for entry in getWatchlist:
            found = re.search(f"title:{ getObject[0].title }", str(entry))
            if found:
                onWatchlist = 1
                break

    if getObject[0].status == "closed":
        if float(currentBid) > 0:
            highestBidder = checkBid.placedBy
            print(highestBidder)
            pass

    # Comments
    try:
        comments = Comment.objects.all()
    except:
        comments = None

    return render(request, "auctions/listing.html", {
        "listing": listingDetails,
        "placeBid": PlaceBid,
        "watchlist": onWatchlist,
        "watchlistLen": len(getWatchlist),
        "message": message,
        "commentForm": CommentForm,
        "comments": comments,
        "highestBidder": highestBidder
    })


def watchlist(request):

    if request.user.is_authenticated:
        # Listing watchlist items
        current_user = request.user
        getWatchlist = Watchlist.objects.filter(user=f'{ current_user.id }')
        watchlist = []
        for entry in getWatchlist:
            try:
                currentBid = Bid.objects.filter(placedTo=Listing.objects.get(
                    title=entry.listing.title)).order_by('-id')[0].amount
            except:
                currentBid = 0

            if entry.listing.startingBid <= currentBid:
                bid = currentBid
            else:
                bid = entry.listing.startingBid
            watchlist.append(
                {
                    "title": entry.listing.title,
                    "description": entry.listing.description,
                    "bid": bid,
                    "category": entry.listing.category,
                    "imageURL": entry.listing.imageURL
                }
            )

    return render(request, "auctions/watchlist.html", {
        "watchlistLen": len(getWatchlist),
        "watchlist": watchlist
    })
