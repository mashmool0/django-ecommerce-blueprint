from django.contrib import admin
from .models import Campaign, MessageOutbox, ShortLink, ShortLinkClick


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "channel", "variant",
                    "is_transactional", "created_at")
    list_filter = ("channel", "is_transactional")
    search_fields = ("name",)


@admin.register(MessageOutbox)
class MessageOutboxAdmin(admin.ModelAdmin):
    list_display = ("phone_e164", "campaign", "status",
                    "provider", "sent_at", "delivered_at")
    list_filter = ("status", "provider")
    search_fields = ("phone_e164", "provider_msg_id")


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ("uuid_code", "campaign", "variant", "created_at")
    search_fields = ("uuid_code",)


@admin.register(ShortLinkClick)
class ShortLinkClickAdmin(admin.ModelAdmin):
    list_display = ("shortlink", "user", "anonymous_id", "clicked_at", "ip")
    list_filter = ("clicked_at",)
    search_fields = ("shortlink__uuid_code",
                     "user__phone_number", "anonymous_id")
