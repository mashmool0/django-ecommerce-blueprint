from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "gateway", "status", "amount_toman",
                    "authority", "ref_id", "created_at")
    list_filter = ("gateway", "status")
    search_fields = ("order__id", "authority", "ref_id")
