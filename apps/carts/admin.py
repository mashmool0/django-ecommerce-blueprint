from django.contrib import admin
from .models import Cart, CartItem, Checkout


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "anonymous_id",
                    "applied_coupon", "updated_at")
    list_filter = ("applied_coupon",)
    search_fields = ("id", "user__phone_number")
    inlines = [CartItemInline]


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "status", "phone_number",
                    "payable_toman", "created_at")
    list_filter = ("status", "payment_method")
    search_fields = ("cart__id", "phone_number")
