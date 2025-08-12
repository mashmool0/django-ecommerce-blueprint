from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UUIDModel
from apps.catalog.models import ProductVariant

# ---------- Event log ----------


class EventLog(UUIDModel):
    """
    Write-once event stream for analytics and attribution.
    Send transactional events to GA4/Mixpanel server-side and mark sent flags.
    """
    name = models.CharField(
        # e.g., Product Viewed, Add to Cart, Order Paid
        _("نام رویداد"), max_length=50)
    timestamp = models.DateTimeField(_("زمان وقوع"), db_index=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True, on_delete=models.SET_NULL)
    anonymous_id = models.UUIDField(null=True, blank=True, db_index=True)
    session_id = models.UUIDField(null=True, blank=True)

    # {utm_source, utm_medium, ...}
    utm_json = models.JSONField(_("UTM"), null=True, blank=True)
    # domain payload (order_id, items, value, fees...)
    properties = models.JSONField(_("خصوصیات"), null=True, blank=True)

    sent_to_ga = models.BooleanField(_("ارسال به GA4"), default=False)
    sent_to_mixpanel = models.BooleanField(
        _("ارسال به Mixpanel"), default=False)

    class Meta:
        verbose_name = _("رویداد")
        verbose_name_plural = _("رویدادها")
        indexes = [
            models.Index(fields=["name", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["anonymous_id", "timestamp"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.name} @ {self.timestamp}"

# ---------- Daily snapshots ----------


class DailyUserSnapshot(models.Model):
    snapshot_date = models.DateField(_("تاریخ"), db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_snapshots")

    total_orders = models.PositiveIntegerField(_("تعداد سفارش"), default=0)
    total_spend_toman = models.BigIntegerField(
        _("مجموع هزینه (تومان)"), default=0)
    first_purchase_at = models.DateTimeField(
        _("اولین خرید"), null=True, blank=True)
    last_purchase_at = models.DateTimeField(
        _("آخرین خرید"), null=True, blank=True)

    rfm_score = models.PositiveSmallIntegerField(
        _("امتیاز RFM"), null=True, blank=True)
    churn_risk = models.CharField(
        _("ریسک ریزش"), max_length=10, null=True, blank=True)

    lifetime_cogs_toman = models.BigIntegerField(
        _("مجموع بهای تمام‌شده"), default=0)
    preferred_categories = models.JSONField(
        _("دسته‌های محبوب (IDs)"), null=True, blank=True)  # optional

    class Meta:
        verbose_name = _("عکس روزانه کاربر")
        verbose_name_plural = _("عکس‌های روزانه کاربر")
        unique_together = [("snapshot_date", "user")]
        indexes = [models.Index(fields=["snapshot_date"]),
                   models.Index(fields=["user"])]

    def __str__(self):
        return f"{self.user_id} @ {self.snapshot_date}"


class DailyInventorySnapshot(models.Model):
    snapshot_date = models.DateField(_("تاریخ"), db_index=True)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="daily_snapshots")

    units_on_hand = models.IntegerField(_("موجودی"))
    inventory_value_toman = models.BigIntegerField(_("ارزش موجودی (تومان)"))
    sell_through_rate = models.DecimalField(
        _("نرخ فروش"), max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = _("عکس روزانه موجودی")
        verbose_name_plural = _("عکس‌های روزانه موجودی")
        unique_together = [("snapshot_date", "variant")]
        indexes = [models.Index(fields=["snapshot_date"]),
                   models.Index(fields=["variant"])]

    def __str__(self):
        return f"{self.variant_id} @ {self.snapshot_date}"
