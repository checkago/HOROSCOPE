from __future__ import annotations

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .article_loader import load_article_stubs_from_disk
from .models import Article


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
