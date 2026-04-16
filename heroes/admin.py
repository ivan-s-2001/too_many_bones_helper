from urllib.parse import urlencode

from django import forms
from django.contrib import admin
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html

from content.models import Block

from .models import Hero, HeroPage, PageSection


def build_admin_changelist_url(url_name: str, **filters) -> str:
    base_url = reverse(url_name)
    if not filters:
        return base_url

    return f'{base_url}?{urlencode(filters)}'


class HeroAdminForm(forms.ModelForm):
    class Meta:
        model = Hero
        fields = '__all__'
        labels = {
            'name': 'Имя героя',
            'slug': 'Slug',
            'tagline': 'Короткий слоган',
            'description': 'Описание',
            'accent': 'Акцент / цвет',
            'order': 'Порядок',
            'is_published': 'Опубликован',
        }
        help_texts = {
            'slug': 'Используется в URL публичной страницы героя.',
            'accent': 'Например: #8b5cf6 или short-code, если вы его уже используете в шаблонах.',
            'order': 'Меньшее значение показывает героя выше в списках.',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }


class HeroPageAdminForm(forms.ModelForm):
    class Meta:
        model = HeroPage
        fields = '__all__'
        labels = {
            'hero': 'Герой',
            'code': 'Код страницы',
            'slug': 'Slug страницы',
            'title': 'Заголовок страницы',
            'tab_label': 'Подпись вкладки',
            'lead': 'Вводный текст',
            'order': 'Порядок',
            'is_published': 'Опубликована',
        }
        help_texts = {
            'code': 'Технический код страницы для шаблонов, логики и дампов.',
            'slug': 'Используется во второй части URL страницы героя.',
            'tab_label': 'Короткая подпись для нижней навигации или табов.',
            'order': 'Меньшее значение показывает страницу раньше.',
        }
        widgets = {
            'lead': forms.Textarea(attrs={'rows': 5}),
        }


class PageSectionAdminForm(forms.ModelForm):
    class Meta:
        model = PageSection
        fields = '__all__'
        labels = {
            'page': 'Страница героя',
            'code': 'Код секции',
            'slug': 'Slug секции',
            'title': 'Заголовок секции',
            'description': 'Описание секции',
            'order': 'Порядок',
            'is_published': 'Опубликована',
        }
        help_texts = {
            'code': 'Технический код секции для шаблонов и данных.',
            'slug': 'Slug можно использовать для якорей и внутренних ссылок.',
            'order': 'Меньшее значение показывает секцию выше на странице.',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class HeroPageInline(admin.TabularInline):
    model = HeroPage
    form = HeroPageAdminForm
    extra = 0
    fields = (
        'title',
        'code',
        'tab_label',
        'order',
        'is_published',
        'sections_count',
        'open_page_admin',
    )
    readonly_fields = ('sections_count', 'open_page_admin')
    ordering = ('order', 'title')
    show_change_link = True
    verbose_name = 'страница героя'
    verbose_name_plural = 'Страницы героя'

    @admin.display(description='Секций')
    def sections_count(self, obj):
        if not obj.pk:
            return '—'
        return obj.sections.count()

    @admin.display(description='Переход')
    def open_page_admin(self, obj):
        if not obj.pk:
            return 'Сначала сохраните героя'
        url = reverse('admin:heroes_heropage_change', args=[obj.pk])
        return format_html('<a href="{}">Открыть страницу</a>', url)


class PageSectionInline(admin.TabularInline):
    model = PageSection
    form = PageSectionAdminForm
    extra = 0
    fields = (
        'title',
        'code',
        'order',
        'is_published',
        'blocks_count',
        'open_section_admin',
    )
    readonly_fields = ('blocks_count', 'open_section_admin')
    ordering = ('order', 'title')
    show_change_link = True
    verbose_name = 'секция страницы'
    verbose_name_plural = 'Секции страницы'

    @admin.display(description='Блоков')
    def blocks_count(self, obj):
        if not obj.pk:
            return '—'
        return obj.blocks.count()

    @admin.display(description='Переход')
    def open_section_admin(self, obj):
        if not obj.pk:
            return 'Сначала сохраните страницу'
        url = reverse('admin:heroes_pagesection_change', args=[obj.pk])
        return format_html('<a href="{}">Открыть секцию</a>', url)


class BlockInline(admin.TabularInline):
    model = Block
    extra = 0
    fields = (
        'title',
        'type',
        'order',
        'is_published',
        'data_preview',
        'open_block_admin',
    )
    readonly_fields = ('data_preview', 'open_block_admin')
    ordering = ('order', 'id')
    show_change_link = True
    verbose_name = 'блок'
    verbose_name_plural = 'Блоки секции'

    @admin.display(description='Краткий JSON')
    def data_preview(self, obj):
        if not obj.pk or not obj.data:
            return '—'

        if isinstance(obj.data, dict):
            preview = ', '.join(obj.data.keys())
        else:
            preview = str(obj.data)

        if len(preview) > 60:
            preview = f'{preview[:57]}...'

        return preview

    @admin.display(description='Переход')
    def open_block_admin(self, obj):
        if not obj.pk:
            return 'Сначала сохраните секцию'
        url = reverse('admin:content_block_change', args=[obj.pk])
        return format_html('<a href="{}">Открыть блок</a>', url)


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    form = HeroAdminForm
    list_display = (
        'name',
        'slug',
        'accent_badge',
        'order',
        'is_published',
        'pages_count',
        'pages_changelist_link',
    )
    search_fields = ('name', 'slug', 'tagline', 'description', 'accent')
    search_help_text = 'Поиск по имени героя, slug, слогану, описанию и акценту.'
    list_filter = ('is_published',)
    ordering = ('order', 'name')
    inlines = (HeroPageInline,)
    readonly_fields = (
        'accent_preview',
        'pages_count',
        'published_pages_count',
        'pages_changelist_link',
        'public_link',
    )
    fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'name',
                    'slug',
                    'tagline',
                ),
            },
        ),
        (
            'Описание и стиль',
            {
                'fields': (
                    'description',
                    'accent',
                    'accent_preview',
                ),
            },
        ),
        (
            'Публикация и структура',
            {
                'fields': (
                    'order',
                    'is_published',
                    'pages_count',
                    'published_pages_count',
                    'pages_changelist_link',
                    'public_link',
                ),
            },
        ),
    )
    save_on_top = True
    list_per_page = 25
    empty_value_display = '—'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _pages_total=Count('pages', distinct=True),
            _pages_published=Count(
                'pages',
                filter=Q(pages__is_published=True),
                distinct=True,
            ),
        )

    @admin.display(description='Акцент', ordering='accent')
    def accent_badge(self, obj):
        if not obj.accent:
            return '—'

        return format_html(
            '<span style="display:inline-flex; align-items:center; gap:8px;">'
            '<span style="width:14px; height:14px; border-radius:999px; '
            'border:1px solid #ccc; background:{};"></span>'
            '<code>{}</code>'
            '</span>',
            obj.accent,
            obj.accent,
        )

    @admin.display(description='Предпросмотр акцента')
    def accent_preview(self, obj):
        if not obj.accent:
            return 'Акцент пока не задан.'

        return format_html(
            '<div style="display:flex; align-items:center; gap:12px;">'
            '<div style="width:32px; height:32px; border-radius:999px; '
            'border:1px solid #ccc; background:{};"></div>'
            '<strong>{}</strong>'
            '</div>',
            obj.accent,
            obj.accent,
        )

    @admin.display(description='Страниц', ordering='_pages_total')
    def pages_count(self, obj):
        return getattr(obj, '_pages_total', obj.pages.count())

    @admin.display(description='Опубликованных страниц', ordering='_pages_published')
    def published_pages_count(self, obj):
        return getattr(
            obj,
            '_pages_published',
            obj.pages.filter(is_published=True).count(),
        )

    @admin.display(description='Переход к страницам')
    def pages_changelist_link(self, obj):
        if not obj.pk:
            return 'Сначала сохраните героя'

        url = build_admin_changelist_url(
            'admin:heroes_heropage_changelist',
            hero__id__exact=obj.pk,
        )
        return format_html(
            '<a href="{}">Открыть страницы героя</a>',
            url,
        )

    @admin.display(description='Публичная страница')
    def public_link(self, obj):
        if not obj.pk:
            return 'Сначала сохраните героя'

        if not obj.is_published:
            return 'Герой ещё не опубликован.'

        has_published_pages = obj.pages.filter(is_published=True).exists()
        if not has_published_pages:
            return 'Нужна хотя бы одна опубликованная страница героя.'

        url = reverse('heroes:detail', args=[obj.slug])
        return format_html('<a href="{}" target="_blank">Открыть на сайте</a>', url)


@admin.register(HeroPage)
class HeroPageAdmin(admin.ModelAdmin):
    form = HeroPageAdminForm
    list_display = (
        'title',
        'hero_link',
        'code',
        'slug',
        'order',
        'is_published',
        'sections_count',
        'sections_changelist_link',
        'public_link',
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
    search_help_text = 'Поиск по странице, её коду, slug, текстам и связанному герою.'
    list_filter = ('is_published', 'hero')
    ordering = ('hero__order', 'order', 'title')
    list_select_related = ('hero',)
    autocomplete_fields = ('hero',)
    inlines = (PageSectionInline,)
    readonly_fields = (
        'hero_link_readonly',
        'sections_count',
        'published_sections_count',
        'sections_changelist_link',
        'public_link',
    )
    fieldsets = (
        (
            'Положение в структуре',
            {
                'fields': (
                    'hero',
                    'hero_link_readonly',
                ),
            },
        ),
        (
            'Основное',
            {
                'fields': (
                    'title',
                    'code',
                    'slug',
                    'tab_label',
                    'lead',
                ),
            },
        ),
        (
            'Публикация и секции',
            {
                'fields': (
                    'order',
                    'is_published',
                    'sections_count',
                    'published_sections_count',
                    'sections_changelist_link',
                    'public_link',
                ),
            },
        ),
    )
    save_on_top = True
    list_per_page = 25
    empty_value_display = '—'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('hero').annotate(
            _sections_total=Count('sections', distinct=True),
            _sections_published=Count(
                'sections',
                filter=Q(sections__is_published=True),
                distinct=True,
            ),
        )

    @admin.display(description='Герой', ordering='hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.hero.name)

    @admin.display(description='Герой')
    def hero_link_readonly(self, obj):
        if not obj.pk:
            return 'Сначала сохраните страницу'
        return self.hero_link(obj)

    @admin.display(description='Секций', ordering='_sections_total')
    def sections_count(self, obj):
        return getattr(obj, '_sections_total', obj.sections.count())

    @admin.display(description='Опубликованных секций', ordering='_sections_published')
    def published_sections_count(self, obj):
        return getattr(
            obj,
            '_sections_published',
            obj.sections.filter(is_published=True).count(),
        )

    @admin.display(description='Переход к секциям')
    def sections_changelist_link(self, obj):
        if not obj.pk:
            return 'Сначала сохраните страницу'

        url = build_admin_changelist_url(
            'admin:heroes_pagesection_changelist',
            page__id__exact=obj.pk,
        )
        return format_html('<a href="{}">Открыть секции страницы</a>', url)

    @admin.display(description='Публичная страница')
    def public_link(self, obj):
        if not obj.pk:
            return 'Сначала сохраните страницу'

        if not obj.hero.is_published or not obj.is_published:
            return 'Для ссылки герой и страница должны быть опубликованы.'

        url = reverse('heroes:page_detail', args=[obj.hero.slug, obj.slug])
        return format_html('<a href="{}" target="_blank">Открыть на сайте</a>', url)


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    form = PageSectionAdminForm
    list_display = (
        'title',
        'page_link',
        'hero_link',
        'code',
        'slug',
        'order',
        'is_published',
        'blocks_count',
        'blocks_changelist_link',
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
    search_help_text = 'Поиск по секции, коду, slug, описанию, странице и герою.'
    list_filter = ('is_published', 'page__hero', 'page')
    ordering = ('page__hero__order', 'page__order', 'order', 'title')
    autocomplete_fields = ('page',)
    inlines = (BlockInline,)
    list_select_related = ('page', 'page__hero')
    readonly_fields = (
        'page_link_readonly',
        'hero_link_readonly',
        'blocks_count',
        'published_blocks_count',
        'blocks_changelist_link',
    )
    fieldsets = (
        (
            'Положение в структуре',
            {
                'fields': (
                    'page',
                    'page_link_readonly',
                    'hero_link_readonly',
                ),
            },
        ),
        (
            'Основное',
            {
                'fields': (
                    'title',
                    'code',
                    'slug',
                    'description',
                ),
            },
        ),
        (
            'Публикация и блоки',
            {
                'fields': (
                    'order',
                    'is_published',
                    'blocks_count',
                    'published_blocks_count',
                    'blocks_changelist_link',
                ),
            },
        ),
    )
    save_on_top = True
    list_per_page = 25
    empty_value_display = '—'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('page', 'page__hero').annotate(
            _blocks_total=Count('blocks', distinct=True),
            _blocks_published=Count(
                'blocks',
                filter=Q(blocks__is_published=True),
                distinct=True,
            ),
        )

    @admin.display(description='Страница', ordering='page__title')
    def page_link(self, obj):
        url = reverse('admin:heroes_heropage_change', args=[obj.page_id])
        return format_html('<a href="{}">{}</a>', url, obj.page.title)

    @admin.display(description='Страница')
    def page_link_readonly(self, obj):
        if not obj.pk:
            return 'Сначала сохраните секцию'
        return self.page_link(obj)

    @admin.display(description='Герой', ordering='page__hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.page.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.page.hero.name)

    @admin.display(description='Герой')
    def hero_link_readonly(self, obj):
        if not obj.pk:
            return 'Сначала сохраните секцию'
        return self.hero_link(obj)

    @admin.display(description='Блоков', ordering='_blocks_total')
    def blocks_count(self, obj):
        return getattr(obj, '_blocks_total', obj.blocks.count())

    @admin.display(description='Опубликованных блоков', ordering='_blocks_published')
    def published_blocks_count(self, obj):
        return getattr(
            obj,
            '_blocks_published',
            obj.blocks.filter(is_published=True).count(),
        )

    @admin.display(description='Переход к блокам')
    def blocks_changelist_link(self, obj):
        if not obj.pk:
            return 'Сначала сохраните секцию'

        url = build_admin_changelist_url(
            'admin:content_block_changelist',
            section__id__exact=obj.pk,
        )
        return format_html('<a href="{}">Открыть блоки секции</a>', url)
