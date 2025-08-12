from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UUIDModel
from apps.catalog.models import Product, ProductVariant, MediaAsset
from apps.orders.models import OrderHeader


class ReviewStatus(models.TextChoices):
    PENDING = "pending", _("در انتظار تأیید")
    APPROVED = "approved", _("تأیید شده")
    REJECTED = "rejected", _("رد شده")


class Review(UUIDModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="reviews")
    # Verified purchase: tie to the order that included this product.
    order = models.ForeignKey(
        OrderHeader, on_delete=models.PROTECT, related_name="reviews")

    rating = models.PositiveSmallIntegerField(
        _("امتیاز"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(_("عنوان"), max_length=120, blank=True)
    content = models.TextField(_("متن"), blank=True)
    status = models.CharField(
        _("وضعیت"), max_length=10, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)

    class Meta:
        verbose_name = _("نظر")
        verbose_name_plural = _("نظرات")
        ordering = ["-created_at"]
        unique_together = [("product", "user", "order")
                           ]  # 1 review per purchase

    def __str__(self):
        return f"Review<{self.product_id}, {self.user_id}, {self.rating}>"


class ReviewMedia(UUIDModel):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="media")
    media = models.ForeignKey(
        MediaAsset, on_delete=models.CASCADE, related_name="review_media")

    class Meta:
        verbose_name = _("تصویر نظر")
        verbose_name_plural = _("تصاویر نظر")


class Wishlist(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="wishlist")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="wishlisted_by")

    class Meta:
        verbose_name = _("علاقه‌مندی")
        verbose_name_plural = _("علاقه‌مندی‌ها")
        unique_together = [("user", "variant")]

    def __str__(self):
        return f"Wishlist<{self.user_id}, {self.variant_id}>"
