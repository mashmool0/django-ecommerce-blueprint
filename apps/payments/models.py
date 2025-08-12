from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import UUIDModel
from apps.orders.models import OrderHeader
from apps.carts.models import Checkout


class PaymentStatus(models.TextChoices):
    INITIATED = "initiated", _("آغاز شده")
    AUTHORIZED = "authorized", _("مجاز")
    CAPTURED = "captured", _("کامل پرداخت شد")
    FAILED = "failed", _("ناموفق")
    REFUNDED = "refunded", _("مسترد")


class Payment(UUIDModel):
    order = models.OneToOneField(
        OrderHeader, on_delete=models.CASCADE, related_name="payment",
        null=True, blank=True
    )
    checkout = models.OneToOneField(
        Checkout, on_delete=models.SET_NULL, related_name="payment",
        null=True, blank=True
    )
    gateway = models.CharField(_("درگاه"), max_length=40, default="zarrinpal")
    status = models.CharField(
        _("وضعیت"), max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED)
    amount_toman = models.PositiveIntegerField(_("مبلغ"))
    gateway_fee_toman = models.PositiveIntegerField(_("کارمزد"), default=0)
    authority = models.CharField(_("Authority"), max_length=100)
    ref_id = models.CharField(
        _("RefID"), max_length=100, null=True, blank=True)
    raw_response = models.JSONField(_("پاسخ خام"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("پرداخت")
        verbose_name_plural = _("پرداخت‌ها")

    def __str__(self):
        return f"Payment<{self.order_id}> {self.status}"
