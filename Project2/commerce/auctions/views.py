from django.contrib.auth import authenticate, login, logout # type: ignore
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AuctionListingForm, BidForm, CommentForm
from .models import User, AuctionListing, Bid, Comment, Watchlist


def index(request):
    listings = AuctionListing.objects.filter(is_active=True)
    
    for listing in listings:
        highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
        listing.current_price = highest_bid.amount if highest_bid else listing.starting_bid

    return render(request, "auctions/index.html", {
        "listings": listings
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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            return redirect("index")  # Redirect to home page or listings page
    else:
        form = AuctionListingForm()

    return render(request, "auctions/create_listing.html", {"form": form})

def listing_detail(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    current_price = listing.current_price()
    comments = listing.comments.all()
    is_watching = request.user.is_authenticated and Watchlist.objects.filter(user=request.user, listing=listing).exists()
    highest_bidder = listing.bids.order_by('-amount').first()

    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "current_price": current_price,
        "comments": comments,
        "is_watching": is_watching,
        "highest_bidder": highest_bidder,
        "bid_form": BidForm(),
        "comment_form": CommentForm(),
    })

@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    form = BidForm(request.POST)

    if form.is_valid():
        bid_amount = form.cleaned_data["amount"]
        current_price = listing.current_price()

        if bid_amount <= current_price:
            messages.error(request, "Your bid must be higher than the current price.")
        else:
            # Create the bid
            Bid.objects.create(listing=listing, bidder=request.user, amount=bid_amount)
            # Add to watchlist if not already there
            watchlist.item, created = Watchlist.objects.get_or_create(user=request.user, listing=listing)

            messages.success(request, "Bid placed succesfully! The listing has been added to your watchlist.")
    return redirect("listing_detail", listing_id=listing_id)

@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    watchlist_entry, created = Watchlist.objects.get_or_create(user=request.user, listing=listing)

    if not created:
        watchlist_entry.delete()
        messages.info(request, "Removed from watchlist.")
    else:
        messages.success(request, "Added to watchlist.")

    return redirect("listing_detail", listing_id=listing_id)

@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)

    if request.user != listing.seller:
        messages.error(request, "You cannot close this auction.")
        return redirect("listing_detail", listing_id=listing_id)

    highest_bid = listing.bids.order_by('-amount').first()
    if highest_bid:
        listing.winner = highest_bid.bidder
    listing.is_active = False
    listing.save()

    messages.success(request, "Auction closed successfully.")
    return redirect("listing_detail", listing_id=listing_id)

@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        Comment.objects.create(listing=listing, user=request.user, content=form.cleaned_data["content"])
        messages.success(request, "Comment added successfully.")

    return redirect("listing_detail", listing_id=listing_id)

@login_required
def watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {"watchlist_items": watchlist_items})
