from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import re

from .models import User, Listing, CreateListing, PlaceBid, Bid, Comment, Watchlist


def index(request):

    watchlistLen = 0
    if request.user.is_authenticated:
        # Watchlist
        current_user = request.user
        getWatchlist = Watchlist.objects.filter(user=f'{ current_user.id }')
        watchlistLen = len(getWatchlist)

    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "watchlistLen": watchlistLen
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
        print(request.POST)
        title = request.POST["title"]
        description = request.POST["description"]
        startingBid = request.POST["startingBid"]
        imageURL = request.POST["imageURL"]
        if imageURL == "":
            imageURL = "https://lh3.googleusercontent.com/proxy/X0JRb9qkKE0HD8VgagrefkLSuNn13NVvYcHmtCu7IROEBmGEcUmD9B_D_Mk_lE6idJQqfHfgd9CAr-x7HZk-3a1GrqXAMwDuKmKm75bB9zX5Fw"
        category = request.POST["category"]
        ls = Listing(title=title, description=description,
                     startingBid=startingBid, imageURL=imageURL, category=category)
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
            watchlistAction = request.POST["watchlistAction"]
            print(request.POST)
            print(watchlistAction)
            current_user = request.user
            if watchlistAction == "add":
                watchlistItem = request.POST["watchlistItem"]
                watchlistUpdate = Watchlist(
                    user=User.objects.get(id=current_user.id), listing=Listing.objects.get(
                        title=watchlistItem))
                watchlistUpdate.save()
            if watchlistAction == "remove":
                watchlistItem = request.POST["watchlistItem"]
                watchlistUpdate = Watchlist.objects.get(
                    user=current_user, listing=Listing.objects.get(title=watchlistItem))
                watchlistUpdate.delete()

    # Listing Information
    current_user = request.user
    getObject = Listing.objects.filter(title=f'{ listingTitle }')
    title = re.findall("title:(.+) imageURL", str(getObject[0]))[0]
    description = re.findall(
        "description:(.+) startingBid", str(getObject[0]), flags=re.DOTALL)[0]
    startingBid = re.findall("startingBid:(.+) category",
                             str(getObject[0]), flags=re.DOTALL)[0]
    category = re.findall("category:(.+)", str(getObject[0]))[0]
    try:
        imageURL = re.findall("imageURL:(.+) description",
                              str(getObject[0]), flags=re.DOTALL)[0]
    except:
        imageURL = "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcRJQ9xu5I_En7x6FYaQ8Mlf2QSMCg1cFAUu7w&usqp=CAU"

    listingDetails = {
        "title": title,
        "description": description,
        "startingBid": startingBid,
        "imageURL": imageURL,
        "category": category
    }

    # Watchlist
    getWatchlist = Watchlist.objects.filter(user=f'{ current_user.id }')
    watchlistLen = len(getWatchlist)
    onWatchlist = 0

    for entry in getWatchlist:
        found = re.search(f"title:{ title }", str(entry))
        if found:
            onWatchlist = 1
            break

    print(onWatchlist)
    return render(request, "auctions/listing.html", {
        "listing": listingDetails,
        "placeBid": PlaceBid,
        "watchlist": onWatchlist,
        "watchlistLen": watchlistLen
    })


def watchlist(request):

    if request.user.is_authenticated:
        # Watchlist
        # Listing Information
        watchlistLen = 0
        current_user = request.user
        getWatchlist = Watchlist.objects.filter(user=f'{ current_user.id }')
        watchlistLen = len(getWatchlist)
        watchlist = []
        print(getWatchlist)
        for entry in getWatchlist:
            print(entry)
            watchlist.append(
                {
                    "title": re.findall("title:(.+) imageURL", str(entry))[0],
                    "description": re.findall(
                        "description:(.+) startingBid", str(entry), flags=re.DOTALL)[0],
                    "startingBid": re.findall("startingBid:(.+) category",
                                              str(entry), flags=re.DOTALL)[0],
                    "category": re.findall("category:(.+)", str(entry))[0],
                    "imageURL": re.findall("imageURL:(.+) description",
                                           str(entry), flags=re.DOTALL)[0]
                }
            )
        print(watchlist)

    return render(request, "auctions/watchlist.html", {
        "watchlistLen": watchlistLen,
        "watchlist": watchlist
    })
