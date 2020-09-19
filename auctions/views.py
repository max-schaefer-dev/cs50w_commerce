from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import re

from .models import User, Listing, CreateListing, SendBid, Bid


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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

    return render(request, "auctions/create_listing.html", {
        "createListing": CreateListing
    })


def listing(request, listingTitle):
    """
    if request.method == "POST":
        print(request.POST)
        title = request.POST["title"]
        description = request.POST["description"]
        startingBid = request.POST["startingBid"]
        imageURL = request.POST["imageURL"]
        category = request.POST["category"]
        ls = Listing(title=title, description=description,
                     startingBid=startingBid, imageURL=imageURL, category=category)
        ls.save()
        """

    getObject = Listing.objects.filter(title=f'{listingTitle}')
    title = re.findall("title:(\\w+)", str(getObject[0]))[0]
    description = re.findall("description:(\\w+)", str(getObject[0]))[0]
    startingBid = re.findall("startingBid:(\\w+)", str(getObject[0]))[0]
    category = re.findall("category:(\\w+)", str(getObject[0]))[0]
    try:
        imageURL = re.findall("imageURL:(\\w+)", str(getObject[0]))[0]
    except:
        imageURL = "https://lh3.googleusercontent.com/proxy/X0JRb9qkKE0HD8VgagrefkLSuNn13NVvYcHmtCu7IROEBmGEcUmD9B_D_Mk_lE6idJQqfHfgd9CAr-x7HZk-3a1GrqXAMwDuKmKm75bB9zX5Fw"

    listingDetails = {
        "title": title,
        "description": description,
        "startingBid": startingBid,
        "imageURL": imageURL,
        "category": category
    }
    return render(request, "auctions/listing.html", {
        "listing": listingDetails,
        "sendBid": SendBid
    })
