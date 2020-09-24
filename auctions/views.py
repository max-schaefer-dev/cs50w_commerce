from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
import re

from .helper import getHighestBidder, getWatchlist, checkForBid

from .models import User, Listing, CreateListing, PlaceBid, Bid, Comment, Watchlist, CommentForm


def index(request):
    try:
        checkBid = Bid.objects.filter(
            placedTo=Listing.objects.get(title=title)).order_by('-id')[0]
        currentBid = re.findall("bid:(.+) on:", str(checkBid))[0]
    except:
        currentBid = 0

    if request.user.is_authenticated:
        watchlist, onwatchlist = getWatchlist(request.user, None)
    else:
        watchlist = ""

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
        "watchlistLen": len(watchlist)
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


def categories(request):
    if request.method == "POST":
        category = Listing.objects.get(category=request.POST["category"])
        return render(request, "auctions/category.html", {
            "category": category
        })

    listings = Listing.objects.all()
    categories = []

    for listing in listings:
        categories.append(listing.category)

    if request.user.is_authenticated:
        watchlist, onwatchlist = getWatchlist(request.user, None)
    else:
        watchlist = ""

    return render(request, "auctions/categories.html", {
        "categories": categories,
        "watchlist": watchlist,
        "watchlistLen": len(watchlist)
    })


def category(request, category):
    if request.user.is_authenticated:
        watchlist, onwatchlist = getWatchlist(request.user, None)
    else:
        watchlist = ""

    lm = []
    ls = Listing.objects.all()

    for listing in ls:
        updatedListing = checkForBid([listing])
        lm.append(updatedListing)

    print(lm)
    return render(request, "auctions/category.html", {
        "listings": lm,
        "category": lm[0]["category"],
        "watchlistLen": len(watchlist)
    })


def create_listing(request):
    if request.method == "POST":
        imageURL = request.POST["imageURL"]
        if imageURL == "":
            imageURL = "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcRJQ9xu5I_En7x6FYaQ8Mlf2QSMCg1cFAUu7w&usqp=CAU"

        ls = Listing(title=request.POST["title"], description=request.POST["description"],
                     startingBid=str(format(float(request.POST["startingBid"]), '.2f')), imageURL=imageURL, category=request.POST["category"], user=request.user, status="opened")
        ls.save()

    if request.user.is_authenticated:
        watchlist, onwatchlist = getWatchlist(request.user, None)
    else:
        watchlist = ""

    return render(request, "auctions/create_listing.html", {
        "createListing": CreateListing,
        "watchlistLen": len(watchlist)
    })


def listing(request, listingTitle):
    if request.method == "POST":
        if request.user.is_authenticated:
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

            # if action is related to watchlist actions
            if action == "watchlist_add" or action == "watchlist_remove":
                if action == "watchlist_add":
                    watchlistUpdate = Watchlist(
                        user=User.objects.get(id=request.user.id), listing=Listing.objects.get(
                            title=request.POST["watchlistItem"]))
                    watchlistUpdate.save()

                if action == "watchlist_remove":
                    watchlistUpdate = Watchlist.objects.get(
                        user=request.user, listing=Listing.objects.get(title=request.POST["watchlistItem"]))
                    watchlistUpdate.delete()

            if action == "bid":
                currentBid = request.POST["currentBid"]
                bidPlaced = request.POST["bid"]
                getObject = Listing.objects.filter(
                    title=f'{ listingTitle }')

                # Look if there is was a bid so far
                updatedListing = checkForBid(getObject)

                # Check for watchlist
                if request.user.is_authenticated:
                    watchlist, onwatchlist = getWatchlist(
                        request.user, getObject)

                if float(bidPlaced) >= float(currentBid):
                    status = "success"
                    message = "Your bid was successfully set!"
                    updateBid = Bid(placedBy=User.objects.get(id=request.user.id), placedTo=Listing.objects.get(
                        title=request.POST["placedTo"]), amount=bidPlaced)
                    updateBid.save()

                else:
                    status = "error"
                    message = "Your bid must be higher than the current price!"

                return render(request, "auctions/listing.html", {
                    "listing": updatedListing,
                    "placeBid": PlaceBid,
                    "watchlist": onwatchlist,
                    "watchlistLen": len(watchlist),
                    "status": status,
                    "message": message
                })

    getObject = Listing.objects.filter(title=f'{ listingTitle }')
    message = ""

    # Check for watchlist
    if request.user.is_authenticated:
        watchlist, onwatchlist = getWatchlist(request.user, getObject)
    else:
        onwatchlist = 0
        watchlist = ""

    # Look if there is was a bid so far
    updatedListing = checkForBid(getObject)

    # Get highestBidder if status == closed
    highestBidder = None
    if updatedListing["status"] == "closed":
        highestBidder = getHighestBidder(updatedListing)

    # Comments
    try:
        comments = Comment.objects.all()
    except:
        comments = None

    return render(request, "auctions/listing.html", {
        "listing": updatedListing,
        "placeBid": PlaceBid,
        "watchlist": onwatchlist,
        "watchlistLen": len(watchlist),
        "message": message,
        "commentForm": CommentForm,
        "comments": comments,
        "highestBidder": highestBidder
    })


def watchlist(request):
    if request.user.is_authenticated:
        # Check for watchlist
        watchlist, onwatchlist = getWatchlist(request.user, None)

        # Listing watchlist items
        current_user = request.user
        getWatchlistItems = Watchlist.objects.filter(
            user=f'{ current_user.id }')
        watchlistItems = []
        for entry in getWatchlistItems:
            try:
                currentBid = Bid.objects.filter(placedTo=Listing.objects.get(
                    title=entry.listing.title)).order_by('-id')[0].amount
            except:
                currentBid = 0

            if entry.listing.startingBid <= currentBid:
                bid = currentBid
            else:
                bid = entry.listing.startingBid
            watchlistItems.append(
                {
                    "title": entry.listing.title,
                    "description": entry.listing.description,
                    "bid": bid,
                    "category": entry.listing.category,
                    "imageURL": entry.listing.imageURL
                }
            )

    return render(request, "auctions/watchlist.html", {
        "watchlistLen": len(watchlist),
        "watchlistItems": watchlistItems
    })
