import json

from django import forms
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .block_editors import FALLBACK_FIELD_ATTR, SUPPORTED_BLOCK_TYPE_PRESENTATIONS, block_editor_registry
from .models import Asset, Block


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'preview_thumb',
        'title',
        'slug',
        'kind',
        'image_size',
        'order',
        'is_published',
    )
    list_editable = ('order', 'is_published')
    search_fields = ('title', 'slug', 'alt')
    list_filter = ('kind', 'is_published')
    ordering = ('kind', 'order', 'title')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('preview', 'width', 'height', 'image_path')
    fieldsets = (
        (
            None,
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
            'Файл',
            {
                'fields': (
                    'image',
                    'preview',
                    'image_path',
                    'width',
                    'height',
                ),
                'description': 'Загружайте изображение через Django admin. Файл будет сохранён внутри MEDIA_ROOT.',
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

    @admin.display(description='Превью')
    def preview_thumb(self, obj):
        if not obj.image:
            return '—'

        return format_html(
            '<img src="{}" alt="{}" style="width:64px;height:64px;object-fit:cover;border-radius:12px;border:1px solid #d9d9d9;">',
            obj.image.url,
            obj.alt or obj.title,
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
            '<img src="{}" alt="{}" style="max-width:280px;width:100%;height:auto;border-radius:18px;border:1px solid #d9d9d9;">',
            obj.image.url,
            obj.alt or obj.title,
        )

    @admin.display(description='Путь в media')
    def image_path(self, obj):
        if not obj.image:
            return 'Файл пока не сохранён.'

        return obj.image.name


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
        help_text='Этот режим используется только для block types, у которых пока нет отдельного человеческого редактора.',
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
            'Поддержанные человеческие редакторы: '
            f'{supported_types}. Для остальных типов ниже автоматически включится технический JSON-режим.'
        )
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
class BlockAdmin(admin.ModelAdmin):
    form = BlockAdminForm
    list_display = (
        'type_badge',
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
    readonly_fields = ('editor_mode_guide', 'data_preview_pretty')
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
                        'type',
                        'title',
                        'variant',
                        'anchor',
                    ),
                },
            ),
            (
                'Редактор содержимого',
                {
                    'fields': (
                        'editor_mode_guide',
                        *editor_fields,
                        'technical_data',
                        'data_preview_pretty',
                    ),
                    'description': (
                        'Для поддержанных block types показываются человеческие поля. '
                        'Если тип пока не реализован, включается аккуратный технический JSON-режим без поломки админки.'
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
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('section', 'section__page', 'section__page__hero')

    @admin.display(description='Тип блока', ordering='type')
    def type_badge(self, obj):
        presentation = SUPPORTED_BLOCK_TYPE_PRESENTATIONS.get(obj.type)
        label = presentation.name if presentation else obj.type
        return format_html(
            '<span style="display:inline-flex;align-items:center;padding:6px 10px;border-radius:999px;background:#f4f5f8;border:1px solid #d9dde6;font-weight:700;">{}</span>',
            label,
        )

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

    @admin.display(description='Кратко по JSON', ordering='data')
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
                'Для этого типа отдельный редактор пока не реализован. Ниже доступно безопасное прямое редактирование JSON.'
            )
        else:
            current_name = 'Тип пока не выбран'
            current_description = 'Выберите тип блока. Форма сразу покажет нужные поля или fallback-режим.'

        return format_html(
            '<div class="tmb-block-editor-guide" '
            'data-block-editor-guide '
            'data-empty-title="Тип пока не выбран" '
            'data-empty-text="Выберите тип блока. Форма сразу покажет нужные поля или fallback-режим." '
            'data-fallback-title="Технический JSON-режим" '
            'data-fallback-text="Для этого типа отдельный редактор пока не реализован. Ниже доступно безопасное прямое редактирование JSON.">'
            '<p class="tmb-block-editor-guide__current-title" data-block-editor-guide-title>{}</p>'
            '<p class="tmb-block-editor-guide__current-text" data-block-editor-guide-text>{}</p>'
            '<div class="tmb-block-editor-guide__badges">{}</div>'
            '</div>',
            current_name,
            current_description,
            mark_safe(supported_badges),
        )

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
