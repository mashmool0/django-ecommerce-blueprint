from django.contrib import admin
from .models import (
    Article, ArticleCategory, Tag, ArticleProduct,
    Page, SeoMeta, SiteSeoDefault
)


class ArticleProductInline(admin.TabularInline):
    model = ArticleProduct
    extra = 0


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title_fa", "slug_en", "category",
                    "status", "published_at")
    list_filter = ("status", "category", "tags")
    search_fields = ("title_fa", "slug_en", "excerpt_fa", "content_rich_fa")
    filter_horizontal = ("tags",)
    inlines = [ArticleProductInline]
    fieldsets = (
        (None, {"fields": ("title_fa", "slug_en",
         "excerpt_fa", "content_rich_fa", "cover_image")}),
        ("انتشار", {"fields": ("status", "published_at",
         "category", "author", "tags")}),
    )


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ("name_fa", "slug_en", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name_fa", "slug_en")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name_fa",)
    search_fields = ("name_fa",)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title_fa", "slug_en", "status", "published_at")
    list_filter = ("status",)
    search_fields = ("title_fa", "slug_en", "body_rich_fa")


@admin.register(SeoMeta)
class SeoMetaAdmin(admin.ModelAdmin):
    list_display = ("entity_type", "entity_id", "meta_title_fa",
                    "meta_robots", "canonical_url")
    list_filter = ("entity_type",)
    search_fields = ("entity_id", "meta_title_fa", "meta_description_fa")


@admin.register(SiteSeoDefault)
class SiteSeoDefaultAdmin(admin.ModelAdmin):
    list_display = ("meta_title_suffix_fa",)
