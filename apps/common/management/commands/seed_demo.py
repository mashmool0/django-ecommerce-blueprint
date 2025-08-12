from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.catalog.models import (
    AllowedWeight, Brand, Category, MediaAsset, Product, ProductVariant, VariantPrice,
    GrindType,
)
from apps.inventory.models import Warehouse, StockItem

class Command(BaseCommand):
    help = "Seeds demo catalog, variants, prices, and stock so you can browse in admin."

    def handle(self, *args, **options):
        # Allowed weights
        for g in (250, 500, 1000):
            AllowedWeight.objects.get_or_create(grams=g, defaults={"is_active": True})

        # Brand & Category
        brand, _ = Brand.objects.get_or_create(
            slug_en="danidor", defaults={"name_fa": "دانیدور", "is_active": True}
        )
        cat, _ = Category.objects.get_or_create(
            slug_en="specialty-coffee",
            defaults={"name_fa": "قهوه‌های ویژه", "parent": None, "is_active": True},
        )

        # Media (optional paths)
        hero_img, _ = MediaAsset.objects.get_or_create(
            file_path="/media/products/yirgacheffe.jpg",
            defaults={"alt_fa": "قهوه اتیوپی یرگاچف"},
        )
        hero_img2, _ = MediaAsset.objects.get_or_create(
            file_path="/media/products/colombia.jpg",
            defaults={"alt_fa": "قهوه کلمبیا سوپریمو"},
        )

        # Product 1
        p1, _ = Product.objects.get_or_create(
            slug_en="ethiopia-yirgacheffe",
            defaults={
                "brand": brand,
                "category": cat,
                "name_fa": "قهوه اتیوپی یرگاچف",
                "short_desc_fa": "طعم‌یادهای گل و مرکبات؛ اسیدیته دلنشین.",
                "long_desc_fa": "برای دم‌آوری‌های دستی عالی است.",
                "cover_image": hero_img,
                "is_active": True,
                "is_featured": True,
            },
        )

        # Variants for product 1
        w250 = AllowedWeight.objects.get(grams=250)
        w500 = AllowedWeight.objects.get(grams=500)
        w1000 = AllowedWeight.objects.get(grams=1000)

        v1, _ = ProductVariant.objects.get_or_create(
            sku="YR-250-WHOLE",
            defaults={
                "product": p1, "weight_grams": w250, "grind_type": GrindType.WHOLE,
                "image": hero_img, "is_default": True, "is_active": True,
            },
        )
        v2, _ = ProductVariant.objects.get_or_create(
            sku="YR-500-MED",
            defaults={
                "product": p1, "weight_grams": w500, "grind_type": GrindType.MEDIUM,
                "image": hero_img, "is_default": False, "is_active": True,
            },
        )
        v3, _ = ProductVariant.objects.get_or_create(
            sku="YR-1000-FINE",
            defaults={
                "product": p1, "weight_grams": w1000, "grind_type": GrindType.FINE,
                "image": hero_img, "is_default": False, "is_active": True,
            },
        )

        # Prices for variants (toman)
        VariantPrice.objects.get_or_create(variant=v1, price_toman=320_000, defaults={"compare_at_toman": 360_000})
        VariantPrice.objects.get_or_create(variant=v2, price_toman=590_000, defaults={"compare_at_toman": 640_000})
        VariantPrice.objects.get_or_create(variant=v3, price_toman=1_140_000, defaults={"compare_at_toman": 1_220_000})

        # Product 2
        p2, _ = Product.objects.get_or_create(
            slug_en="colombia-supremo",
            defaults={
                "brand": brand,
                "category": cat,
                "name_fa": "قهوه کلمبیا سوپریمو",
                "short_desc_fa": "بدنه متوسط، کاکائو و کارامل.",
                "long_desc_fa": "انتخابی همه‌پسند برای اسپرسو و موکاپات.",
                "cover_image": hero_img2,
                "is_active": True,
                "is_featured": False,
            },
        )
        v4, _ = ProductVariant.objects.get_or_create(
            sku="CO-250-MED",
            defaults={
                "product": p2, "weight_grams": w250, "grind_type": GrindType.MEDIUM,
                "image": hero_img2, "is_default": True, "is_active": True,
            },
        )
        VariantPrice.objects.get_or_create(variant=v4, price_toman=300_000, defaults={"compare_at_toman": 330_000})

        # Warehouse & stock
        wh, _ = Warehouse.objects.get_or_create(name="Main Warehouse", defaults={"address": ""})
        for v, qty in [(v1, 40), (v2, 25), (v3, 10), (v4, 60)]:
            StockItem.objects.get_or_create(warehouse=wh, variant=v, defaults={"on_hand": qty, "reserved": 0})

        self.stdout.write(self.style.SUCCESS("✅ Demo data seeded."))
        self.stdout.write(f"Products: {Product.objects.count()}, Variants: {ProductVariant.objects.count()}")
        self.stdout.write(f"Prices: {VariantPrice.objects.count()}, Stock items: {StockItem.objects.count()}")
