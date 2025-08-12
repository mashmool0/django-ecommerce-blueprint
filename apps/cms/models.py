from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UUIDModel
from apps.catalog.models import MediaAsset, Product

# ---------- Blog taxonomy ----------


class ArticleStatus(models.TextChoices):
    DRAFT = "draft", _("پیش‌نویس")
    PUBLISHED = "published", _("منتشر شده")


class ArticleCategory(UUIDModel):
    name_fa = models.CharField(_("نام دسته"), max_length=120)
    slug_en = models.SlugField(_("اسلاگ انگلیسی"), max_length=140, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("دسته مقالات")
        verbose_name_plural = _("دسته‌های مقالات")
        ordering = ["name_fa"]

    def __str__(self):
        return self.name_fa


class Tag(UUIDModel):
    name_fa = models.CharField(_("برچسب"), max_length=80, unique=True)

    class Meta:
        verbose_name = _("برچسب")
        verbose_name_plural = _("برچسب‌ها")
        ordering = ["name_fa"]

    def __str__(self):
        return self.name_fa

# ---------- Blog Article ----------


class Article(UUIDModel):
    category = models.ForeignKey(
        ArticleCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="articles")

    title_fa = models.CharField(_("عنوان"), max_length=180)
    slug_en = models.SlugField(_("اسلاگ انگلیسی"), max_length=180, unique=True)
    excerpt_fa = models.TextField(_("خلاصه"), blank=True)
    content_rich_fa = models.TextField(_("متن کامل"), blank=True)

    cover_image = models.ForeignKey(
        MediaAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="article_covers")

    status = models.CharField(
        _("وضعیت"), max_length=10, choices=ArticleStatus.choices, default=ArticleStatus.DRAFT)
    published_at = models.DateTimeField(
        _("زمان انتشار"), null=True, blank=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")

    class Meta:
        verbose_name = _("مقاله")
        verbose_name_plural = _("مقالات")
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title_fa


class ArticleProduct(UUIDModel):
    """Link articles to products for 'content → commerce' attribution."""
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="linked_products")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="mentioned_in_articles")

    class Meta:
        verbose_name = _("ارتباط مقاله و محصول")
        verbose_name_plural = _("ارتباط‌های مقاله و محصول")
        unique_together = [("article", "product")]

# ---------- Static pages ----------


class PageStatus(models.TextChoices):
    DRAFT = "draft", _("پیش‌نویس")
    PUBLISHED = "published", _("منتشر شده")


class Page(UUIDModel):
    title_fa = models.CharField(_("عنوان"), max_length=180)
    slug_en = models.SlugField(_("اسلاگ انگلیسی"), max_length=180, unique=True)
    body_rich_fa = models.TextField(_("متن صفحه"), blank=True)
    status = models.CharField(
        _("وضعیت"), max_length=10, choices=PageStatus.choices, default=PageStatus.DRAFT)
    published_at = models.DateTimeField(
        _("زمان انتشار"), null=True, blank=True)

    class Meta:
        verbose_name = _("صفحه")
        verbose_name_plural = _("صفحات")
        ordering = ["title_fa"]

    def __str__(self):
        return self.title_fa

# ---------- SEO blocks ----------


class SeoEntityType(models.TextChoices):
    PRODUCT = "product", _("محصول")
    CATEGORY = "category", _("دسته")
    ARTICLE = "article", _("مقاله")
    PAGE = "page", _("صفحه")


class SeoMeta(UUIDModel):
    """Reusable SEO attached to a specific entity by type+id (UUID)."""
    entity_type = models.CharField(
        _("نوع"), max_length=20, choices=SeoEntityType.choices)
    entity_id = models.UUIDField(_("شناسه موجودیت"), db_index=True)

    meta_title_fa = models.CharField(
        _("Meta Title"), max_length=180, blank=True)
    meta_description_fa = models.CharField(
        _("Meta Description"), max_length=300, blank=True)
    meta_robots = models.CharField(_("Robots"), max_length=60, blank=True, help_text=_(
        "مثال: index,follow یا noindex,nofollow"))
    canonical_url = models.URLField(_("URL کانونیکال"), blank=True)

    og_title_fa = models.CharField(_("OG Title"), max_length=180, blank=True)
    og_description_fa = models.CharField(
        _("OG Description"), max_length=300, blank=True)
    og_image = models.ForeignKey(
        MediaAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="seo_og_for")

    class Meta:
        verbose_name = _("سئو")
        verbose_name_plural = _("سئوها")
        unique_together = [("entity_type", "entity_id")]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id}"


class SiteSeoDefault(UUIDModel):
    """Fallback SEO used when an entity lacks SeoMeta."""
    meta_title_suffix_fa = models.CharField(
        _("پسوند عنوان سایت"), max_length=120, blank=True)   # e.g., " | دانیدور"
    default_meta_description_fa = models.CharField(
        _("توضیح پیش‌فرض"), max_length=300, blank=True)
    default_og_image = models.ForeignKey(
        MediaAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="site_default_og")

    class Meta:
        verbose_name = _("سئو پیش‌فرض سایت")
        verbose_name_plural = _("سئوهای پیش‌فرض سایت")

    def __str__(self):
        return "Site SEO Defaults"
