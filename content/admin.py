import json

from django import forms
from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from .block_editors import FALLBACK_FIELD_ATTR, SUPPORTED_BLOCK_TYPE_PRESENTATIONS, block_editor_registry
from .models import Asset, Block


Asset._meta.verbose_name = 'ассет'
Asset._meta.verbose_name_plural = 'Ассеты'
Block._meta.verbose_name = 'блок'
Block._meta.verbose_name_plural = 'Блоки'


class AdminUxMixin:
    save_on_top = True
    list_per_page = 50

    @staticmethod
    def _button(label: str, url: str, variant: str = 'default'):
        return format_html(
            '<a class="tmb-admin-link tmb-admin-link--{}" href="{}">{}</a>',
            variant,
            url,
            label,
        )

    @staticmethod
    def _muted(text: str):
        return format_html('<span class="tmb-admin-muted">{}</span>', text)


class BlockTypeDatalistWidget(forms.TextInput):
    datalist_id = 'tmb-block-type-list'

    def __init__(self, attrs=None):
        merged_attrs = {
            'list': self.datalist_id,
            'placeholder': 'Например: text, cards, checklist',
            'class': 'vTextField',
        }
        if attrs:
            merged_attrs.update(attrs)
        super().__init__(attrs=merged_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs=attrs, renderer=renderer)
        options_html = format_html_join(
            '',
            '<option value="{}">{} — {}</option>',
            ((block_type, block_type, presentation.name) for block_type, presentation in SUPPORTED_BLOCK_TYPE_PRESENTATIONS.items()),
        )
        datalist_html = format_html('<datalist id="{}">{}</datalist>', self.datalist_id, options_html)
        return format_html('{}{}', input_html, datalist_html)


@admin.register(Asset)
class AssetAdmin(AdminUxMixin, admin.ModelAdmin):
    list_display = (
        'preview_thumb',
        'title',
        'kind_badge',
        'usage_summary',
        'image_size',
        'order',
        'is_published',
    )
    list_editable = ('order', 'is_published')
    list_display_links = ('title',)
    search_fields = ('title', 'slug', 'alt')
    search_help_text = 'Поиск по названию, slug и alt-тексту.'
    list_filter = ('kind', 'is_published')
    ordering = ('kind', 'order', 'title')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('preview', 'image_path', 'usage_panel')
    fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'title',
                    'slug',
                    'kind',
                    'alt',
                ),
            },
        ),
        (
            'Файл и предпросмотр',
            {
                'fields': (
                    'image',
                    'preview',
                    'image_path',
                ),
                'description': 'Загрузите изображение. После сохранения здесь же появится превью и путь в media.',
            },
        ),
        (
            'Где используется',
            {
                'fields': ('usage_panel',),
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
        return queryset.annotate(
            hero_usage_total=Count('heroes', distinct=True),
            page_icon_usage_total=Count('hero_pages_with_icon', distinct=True),
        )

    @admin.display(description='Превью')
    def preview_thumb(self, obj):
        if not obj.image:
            return '—'
        return format_html(
            '<img src="{}" alt="{}" style="width:64px;height:64px;object-fit:cover;border-radius:12px;border:1px solid #d9d9d9;">',
            obj.image.url,
            obj.alt or obj.title,
        )

    @admin.display(description='Тип')
    def kind_badge(self, obj):
        return format_html('<span class="tmb-admin-kpi">{}</span>', obj.get_kind_display())

    @admin.display(description='Использование')
    def usage_summary(self, obj):
        return format_html(
            '<span class="tmb-admin-kpi">Герои: {}</span><span class="tmb-admin-kpi">Иконки страниц: {}</span>',
            getattr(obj, 'hero_usage_total', 0),
            getattr(obj, 'page_icon_usage_total', 0),
        )

    @admin.display(description='Размер')
    def image_size(self, obj):
        if not obj.width or not obj.height:
            return '—'
        return f'{obj.width} × {obj.height}'

    @admin.display(description='Предпросмотр')
    def preview(self, obj):
        if not obj.image:
            return 'Изображение пока не загружено.'
        return format_html(
            '<img src="{}" alt="{}" style="max-width:300px;width:100%;height:auto;border-radius:18px;border:1px solid #d9d9d9;">',
            obj.image.url,
            obj.alt or obj.title,
        )

    @admin.display(description='Путь в media')
    def image_path(self, obj):
        if not obj.image:
            return 'Файл пока не сохранён.'
        dimensions = f'{obj.width} × {obj.height}' if obj.width and obj.height else 'Размер появится после сохранения'
        return format_html(
            '<div class="tmb-admin-panel">'
            '<div class="tmb-admin-muted">{}</div>'
            '<div class="tmb-admin-muted">{}</div>'
            '</div>',
            obj.image.name,
            dimensions,
        )

    @admin.display(description='Где используется')
    def usage_panel(self, obj):
        if not obj.pk:
            return 'Сначала сохраните ассет, потом появятся ссылки на связанные сущности.'

        hero_url = reverse('admin:heroes_hero_changelist') + f'?portrait__id__exact={obj.pk}'
        page_icon_url = reverse('admin:heroes_heropage_changelist') + f'?icon__id__exact={obj.pk}'

        return format_html(
            '<div class="tmb-admin-panel">'
            '<div class="tmb-admin-links">{}{}</div>'
            '</div>',
            self._button('Герои с этим портретом', hero_url),
            self._button('Страницы с этой иконкой', page_icon_url),
        )


class BlockAdminForm(forms.ModelForm):
    technical_data = forms.JSONField(
        label='Технический JSON',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 12,
                'style': 'font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; width: 100%;',
                FALLBACK_FIELD_ATTR: 'true',
            }
        ),
        help_text='Используйте только для типов, у которых ещё нет человеческого редактора.',
    )

    class Meta:
        model = Block
        fields = (
            'section',
            'type',
            'title',
            'variant',
            'anchor',
            'order',
            'schema_version',
            'is_published',
        )
        widgets = {
            'type': BlockTypeDatalistWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['section'].label = 'Секция'
        self.fields['type'].label = 'Тип блока'
        self.fields['title'].label = 'Заголовок блока'
        self.fields['variant'].label = 'Вариант'
        self.fields['anchor'].label = 'Якорь'
        self.fields['order'].label = 'Порядок'
        self.fields['schema_version'].label = 'Версия схемы'
        self.fields['is_published'].label = 'Опубликовано'

        supported_types = ', '.join(block_editor_registry.supported_types())
        self.fields['type'].help_text = (
            'Выберите один из поддержанных типов: '
            f'{supported_types}. Для неизвестного типа автоматически включится аккуратный JSON-режим.'
        )
        self.fields['title'].help_text = 'Человеческий заголовок блока. Можно оставить пустым, если он не нужен в шаблоне.'
        self.fields['variant'].help_text = 'Необязательный вариант оформления или подтипа блока.'
        self.fields['anchor'].help_text = 'Необязательный якорь для прямой ссылки внутри страницы героя.'
        self.fields['schema_version'].help_text = 'Техническая версия внутренней схемы JSON.'

        raw_data = self.instance.data if getattr(self.instance, 'pk', None) else {}
        self.initial.setdefault('technical_data', raw_data or {})

        for editor in block_editor_registry.all():
            initial_values = editor.get_initial_from_data(raw_data)
            for field_name in editor.field_order:
                if field_name in initial_values:
                    self.initial.setdefault(field_name, initial_values[field_name])

    def clean(self):
        cleaned_data = super().clean()
        raw_type = str(cleaned_data.get('type') or '').strip()
        normalized_type = raw_type.lower()
        editor = block_editor_registry.get(normalized_type)

        if editor is not None:
            cleaned_data['type'] = normalized_type
            cleaned_data['data'] = editor.build_data_from_cleaned_data(cleaned_data)
        else:
            cleaned_data['type'] = raw_type
            cleaned_data['data'] = cleaned_data.get('technical_data') or {}

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.data = self.cleaned_data.get('data', {})
        if commit:
            instance.save()
            self.save_m2m()
        return instance


for editor in block_editor_registry.all():
    for field_name, field in editor.build_form_fields().items():
        setattr(BlockAdminForm, field_name, field)
        BlockAdminForm.declared_fields[field_name] = field
        BlockAdminForm.base_fields[field_name] = field


@admin.register(Block)
class BlockAdmin(AdminUxMixin, admin.ModelAdmin):
    form = BlockAdminForm
    list_display = (
        'content_label',
        'type_badge',
        'section_link',
        'page_link',
        'hero_link',
        'order',
        'is_published',
        'data_preview',
    )
    list_display_links = ('content_label',)
    list_editable = ('order', 'is_published')
    search_fields = (
        'type',
        'title',
        'variant',
        'anchor',
        'section__title',
        'section__page__title',
        'section__page__tab_label',
        'section__page__hero__name',
    )
    search_help_text = 'Поиск по блоку, секции, странице и герою.'
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
    readonly_fields = ('hierarchy_panel', 'editor_mode_guide', 'data_preview_pretty', 'public_block_link')
    formfield_overrides = {
        models.JSONField: {
            'widget': forms.Textarea(
                attrs={
                    'rows': 12,
                    'style': 'font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; width: 100%;',
                }
            ),
        },
    }

    def get_fieldsets(self, request, obj=None):
        editor_fields = block_editor_registry.all_field_names()
        return (
            (
                'Где находится блок',
                {
                    'fields': (
                        'section',
                        'hierarchy_panel',
                    ),
                },
            ),
            (
                'Главное',
                {
                    'fields': (
                        'type',
                        'title',
                        'variant',
                        'anchor',
                        'public_block_link',
                    ),
                },
            ),
            (
                'Содержимое блока',
                {
                    'fields': (
                        'editor_mode_guide',
                        *editor_fields,
                    ),
                    'description': 'Если тип поддержан, здесь показывается человеческий редактор. Если нет — ниже можно использовать JSON fallback.',
                },
            ),
            (
                'JSON fallback',
                {
                    'fields': ('technical_data',),
                    'classes': ('collapse',),
                },
            ),
            (
                'Что реально сохранится',
                {
                    'fields': ('data_preview_pretty',),
                    'classes': ('collapse',),
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
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('section', 'section__page', 'section__page__hero')

    @admin.display(description='Блок', ordering='title')
    def content_label(self, obj):
        title = obj.title or 'Без заголовка'
        preview = self.data_preview(obj)
        return format_html(
            '<div class="tmb-admin-list-main">'
            '<strong>{}</strong>'
            '<span>{}</span>'
            '</div>',
            title,
            preview if preview != '—' else 'Без содержимого',
        )

    @admin.display(description='Тип блока', ordering='type')
    def type_badge(self, obj):
        presentation = SUPPORTED_BLOCK_TYPE_PRESENTATIONS.get(obj.type)
        label = presentation.name if presentation else obj.type
        return format_html('<span class="tmb-admin-kpi">{}</span>', label)

    @admin.display(description='Секция', ordering='section__title')
    def section_link(self, obj):
        url = reverse('admin:heroes_pagesection_change', args=[obj.section_id])
        return format_html('<a href="{}">{}</a>', url, obj.section.title)

    @admin.display(description='Страница', ordering='section__page__title')
    def page_link(self, obj):
        url = reverse('admin:heroes_heropage_change', args=[obj.section.page_id])
        return format_html('<a href="{}">{}</a>', url, obj.section.page.display_title)

    @admin.display(description='Герой', ordering='section__page__hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.section.page.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.section.page.hero.name)

    @admin.display(description='Кратко по содержимому', ordering='data')
    def data_preview(self, obj):
        if not obj.data:
            return '—'

        if isinstance(obj.data, dict):
            preview_parts = []
            for key, value in list(obj.data.items())[:3]:
                if isinstance(value, list):
                    preview_parts.append(f'{key}: {len(value)}')
                else:
                    preview_parts.append(f'{key}: {value}')
            preview = '; '.join(preview_parts)
        else:
            preview = str(obj.data)

        if len(preview) > 90:
            preview = f'{preview[:87]}...'

        return preview

    @admin.display(description='Где находится блок')
    def hierarchy_panel(self, obj):
        if not obj.pk:
            return 'Сначала сохраните блок, потом появятся ссылки на героя, страницу и секцию.'

        hero = obj.section.page.hero
        page = obj.section.page
        section = obj.section
        hero_url = reverse('admin:heroes_hero_change', args=[hero.pk])
        page_url = reverse('admin:heroes_heropage_change', args=[page.pk])
        section_url = reverse('admin:heroes_pagesection_change', args=[section.pk])
        public_url = reverse('heroes:page_detail', args=[hero.slug, page.slug])

        return format_html(
            '<div class="tmb-admin-panel">'
            '<div class="tmb-admin-path">{} / {} / {}</div>'
            '<div class="tmb-admin-links">{}{}{}{}</div>'
            '</div>',
            hero.name,
            page.display_title,
            section.title,
            self._button('Открыть героя', hero_url),
            self._button('Открыть страницу', page_url),
            self._button('Открыть секцию', section_url),
            self._button('Открыть страницу на сайте ↗', public_url, 'primary'),
        )

    @admin.display(description='Режим редактора')
    def editor_mode_guide(self, obj):
        supported_badges = ''.join(
            format_html(
                '<span class="tmb-block-editor-guide__badge">{}</span>',
                f'{block_type} — {presentation.name}',
            )
            for block_type, presentation in SUPPORTED_BLOCK_TYPE_PRESENTATIONS.items()
        )

        current_type = getattr(obj, 'type', '') or ''
        current_editor = block_editor_registry.get(current_type)
        if current_editor:
            current_name = current_editor.presentation.name
            current_description = current_editor.presentation.description
        elif current_type:
            current_name = 'Технический JSON-режим'
            current_description = (
                'Для этого типа отдельный редактор пока не реализован. Ниже можно безопасно редактировать JSON.'
            )
        else:
            current_name = 'Тип пока не выбран'
            current_description = 'Выберите тип блока. Форма сразу покажет человеческие поля или fallback-режим.'

        return format_html(
            '<div class="tmb-block-editor-guide" '
            'data-block-editor-guide '
            'data-empty-title="Тип пока не выбран" '
            'data-empty-text="Выберите тип блока. Форма сразу покажет человеческие поля или fallback-режим." '
            'data-fallback-title="Технический JSON-режим" '
            'data-fallback-text="Для этого типа отдельный редактор пока не реализован. Ниже можно безопасно редактировать JSON.">'
            '<p class="tmb-block-editor-guide__current-title" data-block-editor-guide-title>{}</p>'
            '<p class="tmb-block-editor-guide__current-text" data-block-editor-guide-text>{}</p>'
            '<div class="tmb-block-editor-guide__badges">{}</div>'
            '</div>',
            current_name,
            current_description,
            mark_safe(supported_badges),
        )

    @admin.display(description='Открыть на сайте')
    def public_block_link(self, obj):
        if not obj.pk:
            return 'Сначала сохраните блок.'

        page_url = reverse('heroes:page_detail', args=[obj.section.page.hero.slug, obj.section.page.slug])
        anchor = obj.anchor or f'section-{obj.section.slug}'
        url = f'{page_url}#{anchor}'
        return self._button('Открыть блок на сайте ↗', url, 'primary')

    @admin.display(description='Текущий JSON')
    def data_preview_pretty(self, obj):
        if not obj.pk:
            return 'После первого сохранения здесь появится форматированный JSON, который реально ушёл в поле data.'

        if not obj.data:
            return 'JSON пока пустой.'

        pretty_json = json.dumps(obj.data, ensure_ascii=False, indent=2)
        return format_html('<pre style="margin:0; white-space:pre-wrap;">{}</pre>', pretty_json)

    class Media:
        css = {
            'all': ('content/admin_block_editor.css',),
        }
        js = ('content/admin_block_editor.js',)
