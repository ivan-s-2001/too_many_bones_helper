from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Hero, HeroPage, PageSection


class HeroPageInline(admin.TabularInline):
    model = HeroPage
    extra = 0
    fields = ('title', 'code', 'slug', 'tab_label', 'icon_key', 'order', 'is_published')
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
    list_display = ('portrait_thumb', 'name', 'slug', 'accent', 'order', 'is_published')
    search_fields = (
        'name',
        'slug',
        'tagline',
        'description',
        'accent',
        'portrait__title',
        'portrait__slug',
        'portrait__alt',
    )
    list_filter = ('is_published',)
    ordering = ('order', 'name')
    list_select_related = ('portrait',)
    autocomplete_fields = ('portrait',)
    readonly_fields = ('portrait_preview',)
    inlines = (HeroPageInline,)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'slug',
                    'portrait',
                    'portrait_preview',
                ),
            },
        ),
        (
            'Описание',
            {
                'fields': (
                    'tagline',
                    'description',
                    'accent',
                ),
            },
        ),
        (
            'Публикация и порядок',
            {
                'fields': (
                    'order',
                    'is_published',
                ),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('portrait')

    @admin.display(description='Портрет')
    def portrait_thumb(self, obj):
        if not obj.portrait or not obj.portrait.image:
            return '—'

        return format_html(
            '<img src="{}" alt="{}" style="width:48px;height:48px;object-fit:cover;border-radius:12px;border:1px solid #d9d9d9;">',
            obj.portrait.image.url,
            obj.portrait.alt or obj.portrait.title or obj.name,
        )

    @admin.display(description='Предпросмотр портрета')
    def portrait_preview(self, obj):
        if not obj.portrait or not obj.portrait.image:
            return 'Портрет пока не выбран.'

        return format_html(
            '<img src="{}" alt="{}" style="max-width:240px;width:100%;height:auto;border-radius:18px;border:1px solid #d9d9d9;">',
            obj.portrait.image.url,
            obj.portrait.alt or obj.portrait.title or obj.name,
        )


@admin.register(HeroPage)
class HeroPageAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'hero',
        'code',
        'slug',
        'icon_key',
        'resolved_icon_key_badge',
        'order',
        'is_published',
    )
    search_fields = (
        'title',
        'code',
        'slug',
        'tab_label',
        'lead',
        'hero__name',
        'hero__slug',
    )
    list_filter = ('hero', 'icon_key', 'is_published')
    ordering = ('hero__name', 'order', 'title')
    list_select_related = ('hero',)
    inlines = (PageSectionInline,)
    fields = (
        'hero',
        'title',
        'code',
        'slug',
        'tab_label',
        'lead',
        'icon_key',
        'resolved_icon_key_badge',
        'order',
        'is_published',
    )
    readonly_fields = ('resolved_icon_key_badge',)

    @admin.display(description='Итоговая иконка')
    def resolved_icon_key_badge(self, obj):
        icon_key = obj.resolved_icon_key
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;border:1px solid #d9d9d9;background:#f7f7fb;font-weight:600;">{}</span>',
            icon_key,
        )


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
