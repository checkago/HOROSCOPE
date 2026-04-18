from django.contrib import admin

from .models import Article, Profile, Relationship


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("code", "display_name", "kind", "gender")
    list_filter = ("kind", "gender")
    search_fields = ("display_name", "name", "code")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "sort_order")
    list_editable = ("sort_order",)
    list_display_links = ("title",)
    search_fields = ("title", "slug", "summary")


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ("source", "target")
    list_select_related = ("source", "target")
    search_fields = ("source__display_name", "target__display_name", "heading")
