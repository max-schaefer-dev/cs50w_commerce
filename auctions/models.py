from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms


class User(AbstractUser):
    pass


class CreateListing(forms.Form):
    title = forms.CharField(max_length=48, label="Title")
    description = forms.CharField(
        widget=forms.Textarea, max_length=210, label="Description")
    startingBid = forms.IntegerField(label="Starting Bid")
    imageURL = forms.CharField(
        max_length=100, label="ImageURL (optional)", required=False)
    category = forms.CharField(max_length=48, label="Category")


class Listing(models.Model):
    title = models.CharField(max_length=48)
    description = models.CharField(max_length=210)
    startingBid = models.IntegerField()
    imageURL = models.CharField(max_length=100)
    category = models.CharField(max_length=48)

    def __str__(self):
        return f"title:{ self.title } imageURL:{ self.imageURL } description:{ self.description } startingBid:{ self.startingBid } category:{ self.category }"


class SendBid(forms.Form):
    bid = forms.IntegerField(label="bid")


class Bid(models.Model):
    pass


class Comment(models.Model):
    pass
