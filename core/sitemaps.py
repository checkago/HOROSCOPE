from __future__ import annotations

from urllib.parse import urlencode

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .article_loader import load_article_stubs_from_disk
from .models import Article, Profile, Relationship
from .url_slugs import profile_public_slug


class StaticPagesSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["index", "about", "article_list"]

    def location(self, item):
        return reverse(item)


class ArticlePagesSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        db_articles = list(Article.objects.only("slug").order_by("sort_order", "slug"))
        if db_articles:
            return db_articles
        return load_article_stubs_from_disk()

    def location(self, item):
        return reverse("article_detail", kwargs={"slug": item.slug})


class CharacteristicPagesSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Profile.objects.only("id", "source_file").order_by("code")

    def location(self, item):
        q = urlencode({"mode": "characteristic", "profile": profile_public_slug(item)})
        return f"{reverse('index')}?{q}"


class RelationshipPagesSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return (
            Relationship.objects.select_related("source", "target")
            .only("id", "source__source_file", "target__source_file")
            .order_by("source__code", "target__code")
        )

    def location(self, item):
        q = urlencode(
            {
                "mode": "relationship",
                "source": profile_public_slug(item.source),
                "target": profile_public_slug(item.target),
            }
        )
        return f"{reverse('index')}?{q}"
