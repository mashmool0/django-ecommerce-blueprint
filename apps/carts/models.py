from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from apps.common.models import UUIDModel
from apps.accounts.models import User
from apps.catalog.models import ProductVariant, Coupon


class Cart(UUIDModel):
    """One active cart per user OR per anonymous visitor."""
    user = models.ForeignKey(User, null=True, blank=True,
                             on_delete=models.CASCADE, related_name="carts")
    anonymous_id = models.UUIDField(
        _("شناسه ناشناس"), null=True, blank=True, db_index=True)
    currency = models.CharField(max_length=4, default="TOM")
    applied_coupon = models.ForeignKey(
        Coupon, null=True, blank=True, on_delete=models.SET_NULL, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("سبد خرید")
        verbose_name_plural = _("سبدهای خرید")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["anonymous_id"]),
        ]

    def __str__(self):
        owner = self.user_id or self.anonymous_id
        return f"Cart<{owner}>"


class CartItem(UUIDModel):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="cart_items")
    qty = models.PositiveIntegerField(_("تعداد"))
    unit_price_snapshot_toman = models.PositiveIntegerField(
        _("قیمت واحد در لحظه"), help_text=_("فقط برای نمایش"))
    line_discount_toman = models.PositiveIntegerField(_("تخفیف خط"), default=0)

    class Meta:
        verbose_name = _("آیتم سبد")
        verbose_name_plural = _("آیتم‌های سبد")
        unique_together = [("cart", "variant")]

    def __str__(self):
        return f"{self.variant.sku} x{self.qty}"


class CheckoutStatus(models.TextChoices):
    STARTED = "started", _("شروع شده")
    ABANDONED = "abandoned", _("ناتمام")
    ORDERED = "ordered", _("سفارش شد")


class Checkout(UUIDModel):
    """Snapshot captured just before redirecting to payment."""
    cart = models.OneToOneField(
        Cart, on_delete=models.CASCADE, related_name="checkout")
    status = models.CharField(
        max_length=12, choices=CheckoutStatus.choices, default=CheckoutStatus.STARTED)

    phone_number = PhoneNumberField(_("شماره تلفن"))
    email = models.EmailField(_("ایمیل"), blank=True, null=True)

    shipping_address_json = models.JSONField(_("آدرس ارسال (JSON)"))
    delivery_option = models.CharField(_("روش ارسال"), max_length=40)
    payment_method = models.CharField(
        _("روش پرداخت"), max_length=40, default="zarrinpal")

    # totals snapshot
    items_subtotal_toman = models.PositiveIntegerField(_("جمع اقلام"))
    discounts_total_toman = models.PositiveIntegerField(_("جمع تخفیف‌ها"))
    global_discount_toman = models.PositiveIntegerField(
        _("تخفیف سراسری"), default=0)
    shipping_fee_toman = models.PositiveIntegerField(_("هزینه ارسال"))
    payable_toman = models.PositiveIntegerField(_("مبلغ پرداخت"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("تسویه حساب")
        verbose_name_plural = _("تسویه حساب‌ها")
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"Checkout<{self.cart_id}> {self.status}"
