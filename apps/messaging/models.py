import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UUIDModel


class Channel(models.TextChoices):
    SMS = "sms", _("پیامک")


class Campaign(UUIDModel):
    name = models.CharField(_("نام کمپین"), max_length=120)
    channel = models.CharField(
        _("کانال"), max_length=10, choices=Channel.choices, default=Channel.SMS)
    template = models.TextField(_("قالب پیام"))  # e.g. "سلام {{name}} ..."
    variant = models.CharField(
        _("ورژن"), max_length=10, blank=True)  # A/B labels like A/B
    is_transactional = models.BooleanField(_("تراکنشی؟"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("کمپین")
        verbose_name_plural = _("کمپین‌ها")

    def __str__(self):
        return self.name


class MessageStatus(models.TextChoices):
    QUEUED = "queued", _("در صف")
    SENT = "sent", _("ارسال شد")
    DELIVERED = "delivered", _("تحویل شد")
    FAILED = "failed", _("ناموفق")


class MessageOutbox(UUIDModel):
    campaign = models.ForeignKey(
        Campaign, null=True, blank=True, on_delete=models.SET_NULL, related_name="messages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                             blank=True, on_delete=models.SET_NULL, related_name="messages")
    phone_e164 = models.CharField(
        _("شماره مقصد"), max_length=16)  # for guests too

    body = models.TextField(_("متن پیام"))
    provider = models.CharField(
        _("ارائه‌دهنده"), max_length=40, default="amoot")
    status = models.CharField(
        _("وضعیت"), max_length=10, choices=MessageStatus.choices, default=MessageStatus.QUEUED)
    provider_msg_id = models.CharField(
        _("شناسه پیام نزد ارائه‌دهنده"), max_length=100, null=True, blank=True)

    sent_at = models.DateTimeField(_("ارسال"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("تحویل"), null=True, blank=True)
    failed_at = models.DateTimeField(_("شکست"), null=True, blank=True)
    error_msg = models.TextField(_("متن خطا"), blank=True)

    shortlink = models.ForeignKey(
        "ShortLink", null=True, blank=True, on_delete=models.SET_NULL, related_name="messages")

    class Meta:
        verbose_name = _("پیام خروجی")
        verbose_name_plural = _("پیام‌های خروجی")
        indexes = [models.Index(fields=["status", "provider"])]

    def __str__(self):
        return f"SMS to {self.phone_e164} [{self.status}]"


class ShortLink(UUIDModel):
    uuid_code = models.UUIDField(
        _("کد"), default=uuid.uuid4, unique=True, editable=False)
    target_url = models.TextField(_("آدرس مقصد"))
    campaign = models.ForeignKey(
        Campaign, null=True, blank=True, on_delete=models.SET_NULL, related_name="shortlinks")
    variant = models.CharField(_("ورژن"), max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("کوتاه‌کننده لینک")
        verbose_name_plural = _("کوتاه‌کننده‌های لینک")

    def __str__(self):
        return f"/t/{self.uuid_code}"


class ShortLinkClick(UUIDModel):
    shortlink = models.ForeignKey(
        ShortLink, on_delete=models.CASCADE, related_name="clicks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True, on_delete=models.SET_NULL)
    anonymous_id = models.UUIDField(null=True, blank=True, db_index=True)
    clicked_at = models.DateTimeField(_("زمان کلیک"), auto_now_add=True)
    utm_json = models.JSONField(_("UTM"), null=True, blank=True)
    ip = models.GenericIPAddressField(_("IP"), null=True, blank=True)
    user_agent = models.TextField(_("کاربر-عامل"), blank=True)

    class Meta:
        verbose_name = _("کلیک روی لینک کوتاه")
        verbose_name_plural = _("کلیک‌های لینک کوتاه")
        indexes = [models.Index(fields=["shortlink", "clicked_at"])]
