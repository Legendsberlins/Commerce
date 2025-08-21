# views.py
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import AuctionListing, User, Bid, Comments
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.db.models import Count
import logging
import re
from datetime import datetime   

logger = logging.getLogger(__name__)
UserModel = get_user_model()

def some_view(request):
    return render(request, "auctions/layout.html", {
        "year": datetime.now().year,
    })

@login_required
def index(request):
    listings = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {"listings":listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if not (username and password): # checks if any field is empty
            return render(request, "auctions/login.html", { 
                "message": "All fields are required.",
                })
        # Check if authentication successful
        if user is not None:
            # block anyone with superuser credentials without stating why
            if user.is_superuser:
                logger.warning(f"Blocked login attempt using superuser credentials from IP {request.META.get('REMOTE_ADDR')}")
                return render(request, "auctions/login.html", {
                    "message": "Invalid username or password" 
                })
            login(request, user)
            print(f"Logged in as {user.username}")
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        form_data = {
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        }
        if not (username and email and first_name and last_name and password and confirmation): # checks if any field is empty
            return render(request, "auctions/register.html", { 
                "message": "All fields are required.",
                "form_data": form_data
            })
        if len(password) < 8:
            return render(request, "auctions/register.html", {
                "message": "Password should be at least 8 characters.",
                "form_data": form_data
            })
        if not password[0].isupper():
            return render(request, "auctions/register.html", {
                "message": "Password must begin with an uppercase",
                "form_data": form_data
            }) 
        
        if not re.search(r"\d", password):
            return render(request, "auctions/register.html", {
                "message": "Password must have at least one number.",
                "formdata": form_data
            })
        
        if not re.search(r"[^A-Za-z0-9]", password):
            return render(request, "auctions/register.html", {
                "message": "Password must have at least one special character.",
                "form_data": form_data
            })
        
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match.",
                "form_data": form_data
            })
        
        # Avoid accidently recreating a superuser
        if UserModel.objects.filter(username=username, is_superuser=True).exists():
            return render(request, "auctions/register.html", {
                "message": "Username already taken"
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username=username, 
                email=email, 
                first_name=first_name, 
                last_name=last_name, 
                password=password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        bid = request.POST["bid"]
        photo_url = request.POST["url"]
        category = request.POST["category"]

        listing = AuctionListing(
            title=title,
            description=description, 
            bid=bid,
            photo_url=photo_url,
            user=request.user,
            is_active=True,
            category=category
        )
        listing.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html")

@login_required
def listing_view(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk = listing_id) # compares listing_id the user clicks on with the id on the primary key
    user = request.user
    in_watchlist = listing in user.watchlist.all()
    bids = Bid.objects.filter(listing=listing).order_by('-amount')
    highest_bid = bids.first()
    is_owner = listing.user == user
    is_winner = not listing.is_active and highest_bid and highest_bid.user
    comment_input = ""
    comments = Comments.objects.filter(listing=listing).order_by('-id')

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "watchlist":
            if in_watchlist:
                user.watchlist.remove(listing)
            else:
                user.watchlist.add(listing)
        elif action == "bid":
            bid_input = request.POST.get("bid")

            if not bid_input:
                messages.error(request, "Enter an amount")
            else:
                try:
                    bid_amount = Decimal(bid_input)
                    if (bid_amount < listing.bid) or (highest_bid and bid_amount < highest_bid.amount):
                        messages.error(request, "Bid must be higher than highest bid")
                    else:
                        new_bid = Bid(user=user, listing=listing, amount=bid_amount)
                        new_bid.save()
                        listing.bid = bid_amount
                        listing.save()
                        messages.success(request, "Successfully bid")
                except InvalidOperation:
                    messages.error(request, "Invalid bid amount")

        elif action == "close":
            if is_owner:
                listing.is_active = False
                listing.save()
        
        elif action == "comment":
            comment_input = request.POST.get("comment")
            if comment_input:
                Comments.objects.create(user=user, listing=listing, comment=comment_input)

        return HttpResponseRedirect(reverse("listing", args=[listing_id]))

    in_watchlist

    context = {
        "listing": listing,
        "in_watchlist": in_watchlist,
        "is_owner": is_owner,
        "is_winner": is_winner,
        "comment": comments
    }
    return render(request, "auctions/listing.html", context)

@login_required
def watchlist(request):
    user = request.user
    watchlist_items = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"watchlist": watchlist_items})

@login_required
def categories(request):
    categories = (
        AuctionListing.objects.values("category")
        .annotate(count=Count("id"))
        .filter(is_active=True)
        .order_by("category")
    )
    return render(request, "auctions/categories.html", {"categories": categories})

@login_required
def category_listings(request, category_name):
    listings = AuctionListing.objects.filter(category=category_name, is_active=True)
    return render(request, "auctions/category_listings.html", {"category": category_name, "listings": listings})