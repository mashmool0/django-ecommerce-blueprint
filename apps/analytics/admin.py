from django.contrib import admin
from .models import EventLog, DailyUserSnapshot, DailyInventorySnapshot


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ("name", "timestamp", "user", "anonymous_id",
                    "sent_to_ga", "sent_to_mixpanel")
    list_filter = ("name", "sent_to_ga", "sent_to_mixpanel")
    search_fields = ("name", "user__phone_number")


@admin.register(DailyUserSnapshot)
class DailyUserSnapshotAdmin(admin.ModelAdmin):
    list_display = ("snapshot_date", "user", "total_orders",
                    "total_spend_toman", "rfm_score", "churn_risk")
    list_filter = ("snapshot_date", "churn_risk")
    search_fields = ("user__phone_number",)


@admin.register(DailyInventorySnapshot)
class DailyInventorySnapshotAdmin(admin.ModelAdmin):
    list_display = ("snapshot_date", "variant", "units_on_hand",
                    "inventory_value_toman", "sell_through_rate")
    list_filter = ("snapshot_date",)
    search_fields = ("variant__sku", "variant__product__name_fa")
