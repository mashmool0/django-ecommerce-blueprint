from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.common.models import UUIDModel
from apps.catalog.models import ProductVariant, Coupon
from apps.carts.models import Checkout  # optional link back to checkout


class OrderStatus(models.TextChoices):
    PENDING = "pending", _("در انتظار")
    AWAITING_PAYMENT = "awaiting_payment", _("در انتظار پرداخت")
    PAID = "paid", _("پرداخت شد")
    PROCESSING = "processing", _("در حال پردازش")
    SHIPPED = "shipped", _("ارسال شد")
    DELIVERED = "delivered", _("تحویل شد")
    CANCELLED = "cancelled", _("لغو شد")
    REFUNDED = "refunded", _("مسترد شد")


class OrderHeader(UUIDModel):
    # optional human-friendly sequence you can fill in programmatically
    order_number = models.PositiveBigIntegerField(
        _("شماره سفارش"), unique=True, null=True, blank=True)

    # who bought
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                             blank=True, on_delete=models.SET_NULL, related_name="orders")
    phone_e164 = models.CharField(_("شماره تماس"), max_length=16)
    email = models.EmailField(_("ایمیل"), null=True, blank=True)

    # addresses & channel
    shipping_address_json = models.JSONField(_("آدرس ارسال"))
    channel = models.CharField(_("کانال"), max_length=20, default="web")

    status = models.CharField(
        _("وضعیت"), max_length=20, choices=OrderStatus.choices, default=OrderStatus.PAID)

    # money snapshots
    subtotal_toman = models.PositiveIntegerField(_("جمع اقلام"))
    discounts_toman = models.PositiveIntegerField(_("جمع تخفیف‌ها"))
    global_discount_toman = models.PositiveIntegerField(
        _("تخفیف سراسری"), default=0)
    shipping_fee_toman = models.PositiveIntegerField(_("هزینه ارسال"))
    tax_toman = models.PositiveIntegerField(_("مالیات"), default=0)
    gateway_fee_toman = models.PositiveIntegerField(
        _("کارمزد درگاه"), default=0)
    refund_amount_toman = models.PositiveIntegerField(
        _("مبلغ استرداد"), default=0)
    total_payable_toman = models.PositiveIntegerField(_("مبلغ پرداختی"))

    # profitability (optional, but helpful)
    cogs_total_toman = models.PositiveIntegerField(
        _("بهای تمام شده کل"), default=0)
    contribution_margin_toman = models.IntegerField(
        _("سود ناخالص مشارکتی"), default=0)

    placed_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    paid_at = models.DateTimeField(_("تاریخ پرداخت"), null=True, blank=True)

    # traceability
    checkout = models.OneToOneField(
        Checkout, null=True, blank=True, on_delete=models.SET_NULL, related_name="order")

    class Meta:
        verbose_name = _("سفارش")
        verbose_name_plural = _("سفارش‌ها")
        ordering = ["-placed_at"]

    def __str__(self):
        return f"Order<{self.pk}>"


class OrderLine(UUIDModel):
    order = models.ForeignKey(
        OrderHeader, on_delete=models.CASCADE, related_name="lines")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="order_lines")

    product_name_fa_snapshot = models.CharField(_("نام محصول"), max_length=180)
    # e.g. {"weight_g":250,"grind":"medium"}
    variant_attrs_snapshot = models.JSONField(
        _("مشخصات گونه"), null=True, blank=True)

    qty = models.PositiveIntegerField(_("تعداد"))
    unit_price_toman = models.PositiveIntegerField(_("قیمت واحد"))
    line_discount_toman = models.PositiveIntegerField(_("تخفیف خط"), default=0)

    unit_cogs_toman = models.PositiveIntegerField(
        _("بهای تمام شده واحد"), default=0)
    unit_shipping_cost_toman = models.PositiveIntegerField(
        _("هزینه ارسال واحد"), default=0)
    unit_weight_g = models.PositiveIntegerField(
        _("وزن (گرم)"), null=True, blank=True)

    class Meta:
        verbose_name = _("آیتم سفارش")
        verbose_name_plural = _("آیتم‌های سفارش")

    def __str__(self):
        return f"{self.variant.sku} x{self.qty}"


class ShipmentStatus(models.TextChoices):
    PENDING = "pending", _("در انتظار ارسال")
    SHIPPED = "shipped", _("ارسال شد")
    DELIVERED = "delivered", _("تحویل شد")
    LOST = "lost", _("مفقود")
    RETURNED = "returned", _("مرجوع")


class Shipment(UUIDModel):
    order = models.ForeignKey(
        OrderHeader, on_delete=models.CASCADE, related_name="shipments")
    status = models.CharField(
        _("وضعیت"), max_length=20, choices=ShipmentStatus.choices, default=ShipmentStatus.PENDING)
    carrier = models.CharField(_("حامل"), max_length=60)
    tracking_number = models.CharField(
        _("کد رهگیری"), max_length=100, null=True, blank=True)
    shipped_at = models.DateTimeField(_("تاریخ ارسال"), null=True, blank=True)
    delivered_at = models.DateTimeField(
        _("تاریخ تحویل"), null=True, blank=True)
    shipping_fee_toman = models.PositiveIntegerField(
        _("هزینه ارسال"), default=0)
    weight_grams = models.PositiveIntegerField(
        _("وزن مرسوله (گرم)"), null=True, blank=True)

    class Meta:
        verbose_name = _("مرسوله")
        verbose_name_plural = _("مرسولات")

    def __str__(self):
        return f"Shipment<{self.order_id}>"


class ReturnStatus(models.TextChoices):
    REQUESTED = "requested", _("درخواست شده")
    APPROVED = "approved", _("تأیید شده")
    REJECTED = "rejected", _("رد شده")
    RECEIVED = "received", _("دریافت شد")
    REFUNDED = "refunded", _("مسترد شد")
    CLOSED = "closed", _("بسته شد")


class ReturnRequest(UUIDModel):
    order = models.ForeignKey(
        OrderHeader, on_delete=models.CASCADE, related_name="returns")
    status = models.CharField(
        _("وضعیت"), max_length=20, choices=ReturnStatus.choices, default=ReturnStatus.REQUESTED)
    reason_code = models.CharField(_("علت"), max_length=40)
    requested_at = models.DateTimeField(_("تاریخ درخواست"), auto_now_add=True)
    approved_at = models.DateTimeField(_("تاریخ تأیید"), null=True, blank=True)
    received_at = models.DateTimeField(
        _("تاریخ دریافت"), null=True, blank=True)
    refunded_at = models.DateTimeField(
        _("تاریخ استرداد"), null=True, blank=True)
    notes = models.TextField(_("توضیحات"), blank=True)

    class Meta:
        verbose_name = _("درخواست مرجوعی")
        verbose_name_plural = _("درخواست‌های مرجوعی")


class ReturnItem(UUIDModel):
    return_request = models.ForeignKey(
        ReturnRequest, on_delete=models.CASCADE, related_name="items")
    order_line = models.ForeignKey(
        OrderLine, on_delete=models.PROTECT, related_name="return_items")
    qty = models.PositiveIntegerField(_("تعداد"))
    condition_note = models.TextField(_("وضعیت/توضیحات"), blank=True)

    class Meta:
        verbose_name = _("آیتم مرجوعی")
        verbose_name_plural = _("آیتم‌های مرجوعی")


class CouponRedemption(UUIDModel):
    """What discount the coupon actually gave on THIS order."""
    coupon = models.ForeignKey(
        Coupon, on_delete=models.PROTECT, related_name="redemptions")
    order = models.ForeignKey(
        OrderHeader, on_delete=models.CASCADE, related_name="coupon_redemptions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True, on_delete=models.SET_NULL)
    discount_applied_toman = models.PositiveIntegerField(_("تخفیف اعمال‌شده"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("ثبت استفاده از کوپن")
        verbose_name_plural = _("ثبت‌های استفاده از کوپن")
        unique_together = [("coupon", "order")]
