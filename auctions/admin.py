from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Listing, User, Bid, Comment

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Listing)
