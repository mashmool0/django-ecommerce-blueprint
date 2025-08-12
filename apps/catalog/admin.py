from .models import GlobalDiscount, Coupon  # top imports if not present
from django.contrib import admin
from .models import Brand, Category, MediaAsset, Product, ProductVariant, VariantPrice, AllowedWeight


@admin.register(AllowedWeight)
class AllowedWeightAdmin(admin.ModelAdmin):
    list_display = ("grams", "is_active")
    list_editable = ("is_active",)
    ordering = ("grams",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name_fa", "slug_en", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name_fa", "slug_en")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_fa", "slug_en", "parent", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name_fa", "slug_en")
    list_filter = ("parent",)


class VariantPriceInline(admin.TabularInline):
    model = VariantPrice
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name_fa", "slug_en", "brand",
                    "category", "is_active", "is_featured")
    list_editable = ("is_active", "is_featured")
    search_fields = ("name_fa", "slug_en")
    list_filter = ("brand", "category")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "weight_grams", "grind_type",
                    "is_active", "is_default", "max_qty_per_order")
    list_editable = ("is_active", "is_default")
    list_filter = ("grind_type", "is_active", "product")
    search_fields = ("sku", "product__name_fa")
    inlines = [VariantPriceInline]


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("file_path", "alt_fa")
    search_fields = ("file_path", "alt_fa")


@admin.register(VariantPrice)
class VariantPriceAdmin(admin.ModelAdmin):
    list_display = ("variant", "price_toman",
                    "compare_at_toman", "starts_at", "ends_at")
    list_filter = ("variant__product",)
    search_fields = ("variant__sku",)


@admin.register(GlobalDiscount)
class GlobalDiscountAdmin(admin.ModelAdmin):
    list_display = ("percent_off", "is_active", "starts_at", "ends_at", "note")
    list_editable = ("is_active",)
    list_filter = ("is_active",)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "type", "value",
                    "is_active", "starts_at", "ends_at")
    list_editable = ("is_active",)
    list_filter = ("type", "is_active")
    search_fields = ("code",)
    filter_horizontal = ("allowed_categories", "allowed_products")
