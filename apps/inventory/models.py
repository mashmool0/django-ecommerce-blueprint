from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import UUIDModel
from apps.catalog.models import ProductVariant


class Warehouse(UUIDModel):
    name = models.CharField(_("نام انبار"), max_length=80)
    address = models.TextField(_("آدرس"), blank=True)

    class Meta:
        verbose_name = _("انبار")
        verbose_name_plural = _("انبارها")

    def __str__(self):
        return self.name


class StockItem(UUIDModel):
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="stocks")
    variant = models.OneToOneField(
        ProductVariant, on_delete=models.CASCADE, related_name="stock")  # single-warehouse
    on_hand = models.IntegerField(_("موجودی"), default=0)
    reserved = models.IntegerField(_("رزرو شده"), default=0)
    reorder_level = models.IntegerField(
        _("حد آستانه سفارش"), null=True, blank=True)

    class Meta:
        verbose_name = _("موجودی")
        verbose_name_plural = _("موجودی‌ها")

    def __str__(self):
        return f"{self.variant.sku} → {self.on_hand} on hand"


class StockReservation(UUIDModel):
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="reservations")
    cart_id = models.UUIDField(_("شناسه سبد"), db_index=True)
    qty = models.PositiveIntegerField(_("تعداد"))
    expires_at = models.DateTimeField(_("انقضا"))

    class Meta:
        verbose_name = _("رزرو موجودی")
        verbose_name_plural = _("رزروهای موجودی")
        indexes = [models.Index(fields=["variant", "expires_at"])]

    def __str__(self):
        return f"{self.variant.sku} x{self.qty}"
