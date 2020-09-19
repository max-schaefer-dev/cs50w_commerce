from django.urls import path

from . import views

app_name = "commerce"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<lTitle>", views.listing, name="listing"),
    path("categories", views.create_listing, name="categories"),
    path("watchlist", views.create_listing, name="watchlist")
]
