import json
from django import forms
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from .models import Block


class BlockAdminForm(forms.ModelForm):
    data = forms.JSONField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 12,
                'style': 'font-family: monospace; width: 100%;',
            }
        ),
        help_text='Введите корректный JSON-объект для данных блока.',
    )

    class Meta:
        model = Block
        fields = '__all__'


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    form = BlockAdminForm
    list_display = (
        'type',
        'section_link',
        'page_link',
        'hero_link',
        'order',
        'is_published',
        'data_preview',
    )
    search_fields = (
        'type',
        'title',
        'variant',
        'anchor',
        'section__title',
        'section__code',
        'section__slug',
        'section__page__title',
        'section__page__code',
        'section__page__slug',
        'section__page__hero__name',
        'section__page__hero__slug',
    )
    list_filter = (
        'is_published',
        'type',
        'section__page__hero',
        'section__page',
        'section',
    )
    ordering = (
        'section__page__hero__name',
        'section__page__order',
        'section__order',
        'order',
        'id',
    )
    autocomplete_fields = ('section',)
    list_select_related = ('section', 'section__page', 'section__page__hero')
    readonly_fields = ('data_preview_pretty',)
    formfield_overrides = {
        models.JSONField: {
            'widget': forms.Textarea(
                attrs={
                    'rows': 12,
                    'style': 'font-family: monospace; width: 100%;',
                }
            ),
        },
    }
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'section',
                    'type',
                    'title',
                    'variant',
                    'anchor',
                ),
            },
        ),
        (
            'Публикация и порядок',
            {
                'fields': (
                    'order',
                    'schema_version',
                    'is_published',
                ),
            },
        ),
        (
            'Данные блока',
            {
                'fields': (
                    'data',
                    'data_preview_pretty',
                ),
                'description': 'Для этого шага используется простой JSON без дополнительного редактора и без валидации схемы.',
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('section', 'section__page', 'section__page__hero')

    @admin.display(description='Section', ordering='section__title')
    def section_link(self, obj):
        url = reverse('admin:heroes_pagesection_change', args=[obj.section_id])
        return format_html('<a href="{}">{}</a>', url, obj.section.title)

    @admin.display(description='Page', ordering='section__page__title')
    def page_link(self, obj):
        url = reverse('admin:heroes_heropage_change', args=[obj.section.page_id])
        return format_html('<a href="{}">{}</a>', url, obj.section.page.title)

    @admin.display(description='Hero', ordering='section__page__hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.section.page.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.section.page.hero.name)

    @admin.display(description='JSON', ordering='data')
    def data_preview(self, obj):
        if not obj.data:
            return '—'

        if isinstance(obj.data, dict):
            preview = ', '.join(f'{key}={value}' for key, value in list(obj.data.items())[:3])
        else:
            preview = str(obj.data)

        if len(preview) > 80:
            preview = f'{preview[:77]}...'

        return preview

    @admin.display(description='Текущий JSON')
    def data_preview_pretty(self, obj):
        if not obj.pk:
            return 'Сначала сохраните объект, после этого здесь появится форматированный предпросмотр JSON.'

        if not obj.data:
            return 'JSON пока пустой.'

        pretty_json = json.dumps(obj.data, ensure_ascii=False, indent=2)
        return format_html('<pre style="margin:0; white-space:pre-wrap;">{}</pre>', pretty_json)
