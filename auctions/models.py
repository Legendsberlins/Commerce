# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

class AuctionListing(models.Model):
    CATEGORY_CHOICES = [
        ("Electronics", "Electronics"),
        ("Books", "Books"),
        ("Clothing", "Clothing"),
        ("Home", "Home"),
        ("Toys", "Toys"),
        ("Other", "Other")
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    photo_url = models.URLField(null = True, blank = True, max_length = 350)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings") #related_name allows you to easily access objects in ORM
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    is_active = models.BooleanField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="Other")

    def __str__(self):
        return f"{self.title} {self.description}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.listing} {self.amount}"

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"{self.user}: {self.listing}: {self.comment}"

