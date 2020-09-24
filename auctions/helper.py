import re

from .models import User, Listing, CreateListing, PlaceBid, Bid, Comment, Watchlist, CommentForm


# Helper functions


def getHighestBidder(listing):
    try:
        checkBid = Bid.objects.filter(placedTo=Listing.objects.get(
            title=listing[0].title)).order_by('-id')[0]
        currentBid = re.findall("bid:(.+) on:", str(checkBid))[0]
    except:
        currentBid = 0

    if listing[0].status == "closed":
        if float(currentBid) > 0:
            highestBidder = checkBid.placedBy

    return highestBidder


def getWatchlist(user, listing):
    # Listing Information
    getWatchlist = ""
    onWatchlist = 0

    getWatchlist = Watchlist.objects.filter(user=f'{ user.id }')

    if listing != None:
        for entry in getWatchlist:
            found = re.search(f"title:{ listing[0].title }", str(entry))
            if found:
                onWatchlist = 1
                break

    return getWatchlist, onWatchlist


def checkForBid(listing):
    # Look if there is was a bid so far
    startingBid = listing[0].startingBid
    try:
        checkBid = Bid.objects.filter(
            placedTo=Listing.objects.get(title=listing[0].title)).order_by('-id')[0]
        currentBid = re.findall("bid:(.+) on:", str(checkBid))[0]
    except:
        currentBid = 0

    if float(startingBid) <= float(currentBid):
        bid = currentBid
    else:
        bid = startingBid

    updatedListing = {
        "title": listing[0].title,
        "description": listing[0].description,
        "bid": bid,
        "imageURL": listing[0].imageURL,
        "category": listing[0].category,
        "createdBy": listing[0].user,
        "status": listing[0].status
    }

    return updatedListing
