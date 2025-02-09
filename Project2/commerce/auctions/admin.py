from django.contrib import admin
from .models import AuctionListing, Bid, Comment

@admin.register(AuctionListing)
class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'starting_bid', 'is_active', 'get_owner')
    list_filter = ('is_active', 'category')
    search_fields = ('title', 'description')

    def get_owner(self, obj):
        return obj.owner.username  # Pastikan owner ada

    get_owner.short_description = 'Owner'  # Memberi label di Admin Panel

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('listing', 'bidder', 'amount', 'timestamp')
    list_filter = ('listing', 'bidder')
    search_fields = ('listing__title', 'bidder__username')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('listing', 'user', 'content', 'timestamp')
    search_fields = ('listing__title', 'user__username', 'content')
