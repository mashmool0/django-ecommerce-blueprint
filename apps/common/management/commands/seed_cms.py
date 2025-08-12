from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import MediaAsset, Product
from apps.cms.models import (
    Article, ArticleCategory, Tag, ArticleProduct,
    Page, SeoMeta, SiteSeoDefault, ArticleStatus, PageStatus, SeoEntityType
)


class Command(BaseCommand):
    help = "Seeds demo blog/category/tags/pages and SEO meta."

    def handle(self, *args, **opts):
        user = User.objects.order_by("date_joined").first()

        cat, _ = ArticleCategory.objects.get_or_create(
            slug_en="brewing-guides", defaults={"name_fa": "راهنمای دم‌آوری"})
        tag1, _ = Tag.objects.get_or_create(name_fa="V60")
        tag2, _ = Tag.objects.get_or_create(name_fa="اسپرسو")

        img, _ = MediaAsset.objects.get_or_create(
            file_path="/media/blog/v60.jpg", defaults={"alt_fa": "V60"})

        a1, _ = Article.objects.get_or_create(
            slug_en="how-to-brew-v60",
            defaults={
                "title_fa": "راهنمای دم‌آوری V60",
                "excerpt_fa": "نکات طلایی برای عصاره‌گیری تمیز و شفاف.",
                "content_rich_fa": "نسبت 1:15، دمای آب 92-94°C، پیش‌دم آوری 30 ثانیه...",
                "cover_image": img,
                "status": ArticleStatus.PUBLISHED,
                "published_at": timezone.now(),
                "category": cat,
                "author": user,
            },
        )
        a1.tags.add(tag1)

        a2, _ = Article.objects.get_or_create(
            slug_en="dialing-in-espresso",
            defaults={
                "title_fa": "دایال‌این اسپرسو",
                "excerpt_fa": "چگونه با آسیاب و دوز بازی کنیم تا طعم ایده‌آل برسد.",
                "content_rich_fa": "شروع با 1:2 در 25-30 ثانیه، سپس تنظیم آسیاب...",
                "status": ArticleStatus.PUBLISHED,
                "published_at": timezone.now(),
                "category": cat,
                "author": user,
            },
        )
        a2.tags.add(tag2)

        # link first product (if exists) to first article
        prod = Product.objects.order_by("-created_at").first()
        if prod:
            ArticleProduct.objects.get_or_create(article=a1, product=prod)

        # static page
        p1, _ = Page.objects.get_or_create(
            slug_en="about",
            defaults={
                "title_fa": "درباره ما",
                "body_rich_fa": "داستان دانیدور و قهوه‌های ما...",
                "status": PageStatus.PUBLISHED,
                "published_at": timezone.now(),
            },
        )

        # SEO meta examples
        SeoMeta.objects.get_or_create(
            entity_type=SeoEntityType.ARTICLE,
            entity_id=a1.id,
            defaults={
                "meta_title_fa": "راهنمای دم‌آوری V60 | دانیدور",
                "meta_description_fa": "نکات کاربردی برای دم‌آوری V60 با طعم‌یادهای تمیز.",
                "meta_robots": "index,follow",
                "canonical_url": f"https://example.com/blog/{a1.slug_en}",
                "og_title_fa": "V60 مثل حرفه‌ای‌ها",
                "og_description_fa": "راهنمای گام به گام با نسبت‌ها و دما.",
                "og_image_id": img.id if img else None,
            },
        )

        SiteSeoDefault.objects.get_or_create(
            meta_title_suffix_fa=" | دانیدور",
            defaults={
                "default_meta_description_fa": "فروشگاه تخصصی قهوه و لوازم دم‌آوری.",
                "default_og_image": img,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            "✅ CMS (blog/pages/SEO) demo seeded."))
