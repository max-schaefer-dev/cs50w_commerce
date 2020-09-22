from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms


class User(AbstractUser):
    pass


class CreateListing(forms.Form):
    title = forms.CharField(max_length=48, label="Title",
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}), max_length=210, label="Description")
    startingBid = forms.FloatField(
        label="Starting Bid", widget=forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}))
    imageURL = forms.CharField(
        max_length=100, label="ImageURL (optional)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.CharField(max_length=48, label="Category",
                               widget=forms.TextInput(attrs={'class': 'form-control'}))


class Listing(models.Model):
    title = models.CharField(max_length=48)
    description = models.CharField(max_length=210)
    startingBid = models.FloatField()
    imageURL = models.CharField(max_length=300)
    category = models.CharField(max_length=48)

    def __str__(self):
        return f"title:{ self.title } imageURL:{ self.imageURL } description:{ self.description } startingBid:{ self.startingBid } category:{ self.category }"


class PlaceBid(forms.Form):
    bid = forms.IntegerField(label="",
                             widget=forms.TextInput(attrs={'placeholder': 'Bid', 'class': 'form-control'}))


class Bid(models.Model):
    placedBy = models.CharField(max_length=50)
    placedTo = models.CharField(max_length=48)


class Watchlist(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="listingWatchlist")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="userWatchlist")

    def __str__(self):
        return f"listing:{self.listing} user:{self.user}"


class Comment(models.Model):
    pass
