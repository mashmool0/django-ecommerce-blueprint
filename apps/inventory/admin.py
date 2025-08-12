from django.contrib import admin
from .models import Warehouse, StockItem, StockReservation


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("variant", "on_hand", "reserved", "reorder_level")
    search_fields = ("variant__sku", "variant__product__name_fa")


@admin.register(StockReservation)
class StockReservationAdmin(admin.ModelAdmin):
    list_display = ("variant", "qty", "expires_at", "cart_id")
    list_filter = ("expires_at",)
    search_fields = ("variant__sku", "cart_id")
