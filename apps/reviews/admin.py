from django.contrib import admin
from .models import Review, ReviewMedia, Wishlist


class ReviewMediaInline(admin.TabularInline):
    model = ReviewMedia
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "order",
                    "rating", "status", "created_at")
    list_filter = ("status", "rating")
    search_fields = ("product__name_fa", "user__phone_number",
                     "order__order_number")
    inlines = [ReviewMediaInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "variant", "created_at")
    search_fields = ("user__phone_number", "variant__sku")
