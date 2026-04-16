from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Hero, HeroPage, PageSection


class HeroPageInline(admin.TabularInline):
    model = HeroPage
    extra = 0
    fields = ('title', 'code', 'slug', 'tab_label', 'order', 'is_published')
    ordering = ('order', 'title')
    show_change_link = True


class PageSectionInline(admin.TabularInline):
    model = PageSection
    extra = 0
    fields = ('title', 'code', 'slug', 'order', 'is_published')
    ordering = ('order', 'title')
    show_change_link = True


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'accent', 'order', 'is_published')
    search_fields = ('name', 'slug', 'tagline', 'description', 'accent')
    list_filter = ('is_published',)
    ordering = ('order', 'name')
    inlines = (HeroPageInline,)


@admin.register(HeroPage)
class HeroPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'hero', 'code', 'slug', 'order', 'is_published')
    search_fields = (
        'title',
        'code',
        'slug',
        'tab_label',
        'lead',
        'hero__name',
        'hero__slug',
    )
    list_filter = ('hero', 'is_published')
    ordering = ('hero__name', 'order', 'title')
    list_select_related = ('hero',)
    inlines = (PageSectionInline,)


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'code',
        'page_link',
        'hero_link',
        'order',
        'is_published',
    )
    search_fields = (
        'title',
        'code',
        'slug',
        'description',
        'page__title',
        'page__code',
        'page__slug',
        'page__hero__name',
        'page__hero__slug',
    )
    list_filter = ('is_published', 'page__hero', 'page')
    ordering = ('page__hero__name', 'page__order', 'order', 'title')
    autocomplete_fields = ('page',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('page', 'page__hero')

    @admin.display(description='Page', ordering='page__title')
    def page_link(self, obj):
        url = reverse('admin:heroes_heropage_change', args=[obj.page_id])
        return format_html('<a href="{}">{}</a>', url, obj.page.title)

    @admin.display(description='Hero', ordering='page__hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.page.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.page.hero.name)
