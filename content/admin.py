import json
from urllib.parse import urlencode

from django import forms
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from .models import Block


def build_admin_changelist_url(url_name: str, **filters) -> str:
    base_url = reverse(url_name)
    if not filters:
        return base_url

    return f'{base_url}?{urlencode(filters)}'


class BlockAdminForm(forms.ModelForm):
    data = forms.JSONField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 18,
                'style': 'font-family: ui-monospace, SFMono-Regular, Menlo, monospace; width: 100%;',
            }
        ),
        help_text='Введите корректный JSON. Большие данные лучше редактировать аккуратно и проверять после сохранения.',
    )

    class Meta:
        model = Block
        fields = '__all__'
        labels = {
            'section': 'Секция',
            'type': 'Тип блока',
            'title': 'Заголовок блока',
            'variant': 'Вариант',
            'anchor': 'Якорь',
            'order': 'Порядок',
            'schema_version': 'Версия схемы',
            'data': 'JSON-данные',
            'is_published': 'Опубликован',
        }
        help_texts = {
            'type': 'Например: hero_stats, markdown, gallery и т.п.',
            'title': 'Необязательный заголовок, если он нужен в редакторском интерфейсе.',
            'variant': 'Вариант отображения блока, если он предусмотрен шаблонами.',
            'anchor': 'Необязательный slug для внутренней навигации по странице.',
            'order': 'Меньшее значение показывает блок выше внутри секции.',
        }
        widgets = {
            'title': forms.TextInput(attrs={'style': 'width: 40em;'}),
            'variant': forms.TextInput(attrs={'style': 'width: 30em;'}),
            'anchor': forms.TextInput(attrs={'style': 'width: 30em;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.data:
            self.initial['data'] = json.dumps(
                self.instance.data,
                ensure_ascii=False,
                indent=2,
            )


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    form = BlockAdminForm
    list_display = (
        'type',
        'title_or_type',
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
    search_help_text = 'Поиск по типу блока, заголовку, варианту, якорю и всей иерархии секция → страница → герой.'
    list_filter = (
        'is_published',
        'type',
        'section__page__hero',
        'section__page',
        'section',
    )
    ordering = (
        'section__page__hero__order',
        'section__page__order',
        'section__order',
        'order',
        'id',
    )
    autocomplete_fields = ('section',)
    list_select_related = ('section', 'section__page', 'section__page__hero')
    readonly_fields = (
        'hierarchy_links',
        'section_blocks_link',
        'data_preview_pretty',
    )
    formfield_overrides = {
        models.JSONField: {
            'widget': forms.Textarea(
                attrs={
                    'rows': 18,
                    'style': 'font-family: ui-monospace, SFMono-Regular, Menlo, monospace; width: 100%;',
                }
            ),
        },
    }
    fieldsets = (
        (
            'Положение в структуре',
            {
                'fields': (
                    'section',
                    'hierarchy_links',
                    'section_blocks_link',
                ),
            },
        ),
        (
            'Идентификация блока',
            {
                'fields': (
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
                'description': (
                    'В списке показывается только короткий preview JSON, '
                    'а здесь остаётся полный редактируемый объект и форматированный предпросмотр.'
                ),
            },
        ),
    )
    save_on_top = True
    list_per_page = 30
    empty_value_display = '—'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('section', 'section__page', 'section__page__hero')

    @admin.display(description='Заголовок')
    def title_or_type(self, obj):
        return obj.title or '—'

    @admin.display(description='Секция', ordering='section__title')
    def section_link(self, obj):
        url = reverse('admin:heroes_pagesection_change', args=[obj.section_id])
        return format_html('<a href="{}">{}</a>', url, obj.section.title)

    @admin.display(description='Страница', ordering='section__page__title')
    def page_link(self, obj):
        url = reverse('admin:heroes_heropage_change', args=[obj.section.page_id])
        return format_html('<a href="{}">{}</a>', url, obj.section.page.title)

    @admin.display(description='Герой', ordering='section__page__hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.section.page.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.section.page.hero.name)

    @admin.display(description='Краткий JSON')
    def data_preview(self, obj):
        if not obj.data:
            return '—'

        if isinstance(obj.data, dict):
            preview_parts = []
            for index, (key, value) in enumerate(obj.data.items()):
                if index == 3:
                    break

                rendered_value = json.dumps(value, ensure_ascii=False)
                preview_parts.append(f'{key}={rendered_value}')

            preview = ', '.join(preview_parts)
        else:
            preview = json.dumps(obj.data, ensure_ascii=False)

        if len(preview) > 120:
            preview = f'{preview[:117]}...'

        return format_html('<code>{}</code>', preview)

    @admin.display(description='Иерархия')
    def hierarchy_links(self, obj):
        if not obj.pk:
            return 'Сначала сохраните блок'

        hero_url = reverse('admin:heroes_hero_change', args=[obj.section.page.hero_id])
        page_url = reverse('admin:heroes_heropage_change', args=[obj.section.page_id])
        section_url = reverse('admin:heroes_pagesection_change', args=[obj.section_id])

        return format_html(
            '<a href="{}">{}</a> &rarr; '
            '<a href="{}">{}</a> &rarr; '
            '<a href="{}">{}</a>',
            hero_url,
            obj.section.page.hero.name,
            page_url,
            obj.section.page.title,
            section_url,
            obj.section.title,
        )

    @admin.display(description='Другие блоки этой секции')
    def section_blocks_link(self, obj):
        if not obj.pk:
            return 'Сначала сохраните блок'

        url = build_admin_changelist_url(
            'admin:content_block_changelist',
            section__id__exact=obj.section_id,
        )
        return format_html('<a href="{}">Открыть все блоки этой секции</a>', url)

    @admin.display(description='Форматированный JSON')
    def data_preview_pretty(self, obj):
        if not obj.pk:
            return 'Сначала сохраните объект, после этого здесь появится форматированный JSON.'

        if not obj.data:
            return 'JSON пока пустой.'

        pretty_json = json.dumps(obj.data, ensure_ascii=False, indent=2)
        return format_html('<pre style="margin:0; white-space:pre-wrap;">{}</pre>', pretty_json)
