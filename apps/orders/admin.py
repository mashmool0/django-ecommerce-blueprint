from django.contrib import admin
from .models import (
    OrderHeader, OrderLine, Shipment,
    ReturnRequest, ReturnItem, CouponRedemption
)


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0


class ShipmentInline(admin.TabularInline):
    model = Shipment
    extra = 0


@admin.register(OrderHeader)
class OrderHeaderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_number", "status", "phone_e164",
                    "total_payable_toman", "placed_at", "paid_at")
    list_filter = ("status", "channel")
    search_fields = ("id", "order_number", "phone_e164", "email")
    inlines = [OrderLineInline, ShipmentInline]


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "carrier",
                    "tracking_number", "shipping_fee_toman")


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "reason_code", "requested_at")
    list_filter = ("status",)
    search_fields = ("order__id",)


@admin.register(ReturnItem)
class ReturnItemAdmin(admin.ModelAdmin):
    list_display = ("return_request", "order_line", "qty")


@admin.register(CouponRedemption)
class CouponRedemptionAdmin(admin.ModelAdmin):
    list_display = ("coupon", "order", "user",
                    "discount_applied_toman", "created_at")
    search_fields = ("coupon__code", "order__id", "user__phone_number")
