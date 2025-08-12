from django.db.models.functions import Lower  # add at top if missing
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import UUIDModel

# ---------- Reference / constraints ----------


class AllowedWeight(models.Model):
    """Controls which weights (in grams) are allowed site-wide."""
    grams = models.PositiveIntegerField(primary_key=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("وزن مجاز (گرم)")
        verbose_name_plural = _("وزن‌های مجاز (گرم)")

    def __str__(self):
        return f"{self.grams} g"


class GrindType(models.TextChoices):
    WHOLE = "whole", _("دانه کامل")
    EXTRA_FINE = "extra_fine", _("بسیار ریز")
    FINE = "fine", _("ریز")
    MEDIUM = "medium", _("متوسط")
    COARSE = "coarse", _("درشت")

# ---------- Core catalog ----------


class Brand(UUIDModel):
    name_fa = models.CharField(_("نام برند"), max_length=120)
    slug_en = models.SlugField(_("اسلاگ انگلیسی"), max_length=140, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("برند")
        verbose_name_plural = _("برندها")
        ordering = ["name_fa"]

    def __str__(self):
        return self.name_fa


class Category(UUIDModel):
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    name_fa = models.CharField(_("نام دسته"), max_length=120)
    slug_en = models.SlugField(_("اسلاگ انگلیسی"), max_length=140, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("دسته‌بندی")
        verbose_name_plural = _("دسته‌بندی‌ها")
        ordering = ["name_fa"]

    def __str__(self):
        return self.name_fa


class MediaAsset(UUIDModel):
    file_path = models.CharField(_("مسیر فایل"), max_length=255)
    alt_fa = models.CharField(_("متن جایگزین"), max_length=180, blank=True)

    class Meta:
        verbose_name = _("رسانه")
        verbose_name_plural = _("رسانه‌ها")

    def __str__(self):
        return self.file_path


class Product(UUIDModel):
    brand = models.ForeignKey(Brand, null=True, blank=True,
                              on_delete=models.SET_NULL, related_name="products")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products")
    name_fa = models.CharField(_("نام محصول"), max_length=180)
    slug_en = models.SlugField(_("اسلاگ انگلیسی"), max_length=180, unique=True)
    short_desc_fa = models.TextField(_("توضیح کوتاه"), blank=True)
    long_desc_fa = models.TextField(_("توضیح کامل"), blank=True)
    attributes_json = models.JSONField(
        _("ویژگی‌ها (JSON)"), blank=True, null=True)
    cover_image = models.ForeignKey(
        MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="cover_for")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("محصول")
        verbose_name_plural = _("محصولات")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name_fa


class ProductVariant(UUIDModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(_("SKU"), max_length=60, unique=True)
    barcode = models.CharField(
        _("بارکد"), max_length=64, blank=True, null=True, unique=True)
    weight_grams = models.ForeignKey(
        AllowedWeight, on_delete=models.PROTECT, related_name="variants")
    grind_type = models.CharField(
        _("نوع آسیاب"), max_length=20, choices=GrindType.choices, blank=True, null=True)
    image = models.ForeignKey(MediaAsset, null=True, blank=True,
                              on_delete=models.SET_NULL, related_name="variant_for")
    is_default = models.BooleanField(default=False)
    min_qty_per_order = models.PositiveIntegerField(default=1)
    max_qty_per_order = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("گونه (SKU)")
        verbose_name_plural = _("گونه‌ها (SKU)")
        indexes = [models.Index(fields=["product", "is_active"])]

    def __str__(self):
        g = dict(GrindType.choices).get(self.grind_type, "")
        return f"{self.product.name_fa} — {self.weight_grams} — {g or '—'}"


class VariantPrice(UUIDModel):
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="prices")
    price_toman = models.PositiveIntegerField(_("قیمت (تومان)"))
    compare_at_toman = models.PositiveIntegerField(
        _("قیمت قبل (تومان)"), null=True, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("قیمت گونه")
        verbose_name_plural = _("قیمت‌های گونه")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.variant.sku} : {self.price_toman:,} T"


# ---------- Promotions ----------


class GlobalDiscount(UUIDModel):
    """Site-wide percentage off (e.g., Nowruz sale)."""
    percent_off = models.PositiveSmallIntegerField(
        _("درصد تخفیف"), help_text=_("0 تا 100"))
    is_active = models.BooleanField(default=False)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=140, blank=True)

    class Meta:
        verbose_name = _("تخفیف سراسری")
        verbose_name_plural = _("تخفیف‌های سراسری")

    def __str__(self):
        return f"{self.percent_off}% {'ON' if self.is_active else 'OFF'}"


class CouponType(models.TextChoices):
    PERCENT = "percent", _("درصدی")
    FIXED = "fixed", _("مبلغ ثابت")


class Coupon(UUIDModel):
    code = models.CharField(_("کد"), max_length=40, unique=True)
    type = models.CharField(_("نوع"), max_length=10,
                            choices=CouponType.choices)
    value = models.PositiveIntegerField(
        _("مقدار"), help_text=_("تومان برای ثابت، درصد برای درصدی"))
    min_order_total = models.PositiveIntegerField(
        _("حداقل جمع سبد"), null=True, blank=True)

    # usage limits
    max_uses_total = models.PositiveIntegerField(
        _("حداکثر استفاده کلی"), null=True, blank=True)
    max_uses_per_user = models.PositiveIntegerField(
        _("حداکثر استفاده هر کاربر"), null=True, blank=True)

    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # scope (allow listing) – you can extend with exclusions later
    allowed_categories = models.ManyToManyField(
        Category, blank=True, related_name="coupons")
    allowed_products = models.ManyToManyField(
        Product, blank=True, related_name="coupons")

    class Meta:
        verbose_name = _("کوپن")
        verbose_name_plural = _("کوپن‌ها")
        constraints = [
            models.UniqueConstraint(
                Lower("code"),
                name="coupon_code_case_insensitive_unique",
                violation_error_message=_("کد کوپن تکراری است."),
            )
        ]

    def __str__(self):
        return self.code.upper()
