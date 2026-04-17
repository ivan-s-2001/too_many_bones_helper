from urllib.parse import urlencode

from django.contrib import admin
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html

from content.models import Block

from .models import Hero, HeroPage, PageSection


admin.site.site_header = 'Too Many Bones Helper — редакторская панель'
admin.site.site_title = 'TMB Admin'
admin.site.index_title = 'Структура проекта и контент'

Hero._meta.verbose_name = 'герой'
Hero._meta.verbose_name_plural = 'Герои'
HeroPage._meta.verbose_name = 'страница героя'
HeroPage._meta.verbose_name_plural = 'Страницы героев'
PageSection._meta.verbose_name = 'секция страницы'
PageSection._meta.verbose_name_plural = 'Секции страниц'


class AdminUxMixin:
    save_on_top = True
    list_per_page = 50

    @staticmethod
    def _change_url(admin_name: str, object_id: int) -> str:
        return reverse(admin_name, args=[object_id])

    @staticmethod
    def _changelist_url(admin_name: str, **filters) -> str:
        url = reverse(admin_name)
        clean_filters = {key: value for key, value in filters.items() if value not in (None, '', [])}
        if clean_filters:
            return f'{url}?{urlencode(clean_filters)}'
        return url

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


class HeroPageInline(admin.TabularInline):
    model = HeroPage
    extra = 0
    fields = ('title', 'navigation_label_preview', 'code', 'order', 'is_published', 'open_public_page')
    ordering = ('order', 'title')
    show_change_link = True
    readonly_fields = ('navigation_label_preview', 'open_public_page')
    verbose_name = 'Страница героя'
    verbose_name_plural = 'Страницы героя'

    @admin.display(description='Как видно в навигации')
    def navigation_label_preview(self, obj):
        if not obj.pk:
            return 'Сначала сохраните страницу.'
        return obj.navigation_label

    @admin.display(description='Открыть на сайте')
    def open_public_page(self, obj):
        if not obj.pk:
            return '—'
        url = reverse('heroes:page_detail', args=[obj.hero.slug, obj.slug])
        return format_html('<a href="{}" target="_blank" rel="noreferrer">Страница ↗</a>', url)


class PageSectionInline(admin.TabularInline):
    model = PageSection
    extra = 0
    fields = ('title', 'order', 'is_published', 'blocks_link')
    ordering = ('order', 'title')
    show_change_link = True
    readonly_fields = ('blocks_link',)
    verbose_name = 'Секция страницы'
    verbose_name_plural = 'Секции страницы'

    @admin.display(description='Блоки')
    def blocks_link(self, obj):
        if not obj.pk:
            return 'Сначала сохраните секцию.'
        url = reverse('admin:content_block_changelist')
        return format_html('<a href="{}?section__id__exact={}">Открыть блоки</a>', url, obj.pk)


class BlockInline(admin.TabularInline):
    model = Block
    extra = 0
    fields = ('content_label', 'type', 'order', 'is_published')
    ordering = ('order', 'id')
    show_change_link = True
    readonly_fields = ('content_label',)
    verbose_name = 'Блок'
    verbose_name_plural = 'Блоки секции'

    @admin.display(description='Блок')
    def content_label(self, obj):
        return obj.title or 'Без заголовка'


@admin.register(Hero)
class HeroAdmin(AdminUxMixin, admin.ModelAdmin):
    list_display = (
        'portrait_thumb',
        'name',
        'tagline_short',
        'content_stats',
        'open_pages_admin',
        'open_public_hero',
        'order',
        'is_published',
    )
    list_editable = ('order', 'is_published')
    list_display_links = ('name',)
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
    search_help_text = 'Поиск по герою, портрету и описанию.'
    list_filter = ('is_published',)
    ordering = ('order', 'name')
    list_select_related = ('portrait',)
    autocomplete_fields = ('portrait',)
    readonly_fields = ('portrait_preview', 'structure_panel')
    inlines = (HeroPageInline,)
    fieldsets = (
        (
            'Главное',
            {
                'fields': (
                    'name',
                    'slug',
                    'structure_panel',
                ),
            },
        ),
        (
            'Визуальный образ героя',
            {
                'fields': (
                    'portrait',
                    'portrait_preview',
                    'accent',
                ),
            },
        ),
        (
            'Коротко о герое',
            {
                'fields': (
                    'tagline',
                    'description',
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
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('portrait').annotate(
            page_total=Count('pages', distinct=True),
            section_total=Count('pages__sections', distinct=True),
            block_total=Count('pages__sections__blocks', distinct=True),
            published_page_total=Count('pages', filter=Q(pages__is_published=True), distinct=True),
        )

    @admin.display(description='Портрет')
    def portrait_thumb(self, obj):
        if not obj.portrait or not obj.portrait.image:
            return '—'
        return format_html(
            '<img src="{}" alt="{}" style="width:48px;height:48px;object-fit:cover;border-radius:12px;border:1px solid #d9d9d9;">',
            obj.portrait.image.url,
            obj.portrait.alt or obj.portrait.title or obj.name,
        )

    @admin.display(description='Тэглайн')
    def tagline_short(self, obj):
        return obj.tagline or self._muted('Не заполнен')

    @admin.display(description='Структура')
    def content_stats(self, obj):
        return format_html(
            '<span class="tmb-admin-kpi">{}</span><span class="tmb-admin-kpi">{}</span><span class="tmb-admin-kpi">{}</span>',
            f'Страниц: {getattr(obj, "page_total", 0)}',
            f'Секций: {getattr(obj, "section_total", 0)}',
            f'Блоков: {getattr(obj, "block_total", 0)}',
        )

    @admin.display(description='Страницы героя')
    def open_pages_admin(self, obj):
        url = self._changelist_url('admin:heroes_heropage_changelist', hero__id__exact=obj.pk)
        return self._button('Открыть страницы', url)

    @admin.display(description='Сайт')
    def open_public_hero(self, obj):
        url = reverse('heroes:detail', args=[obj.slug])
        return self._button('Открыть героя ↗', url, 'primary')

    @admin.display(description='Предпросмотр портрета')
    def portrait_preview(self, obj):
        if not obj.portrait or not obj.portrait.image:
            return 'Портрет пока не выбран.'
        return format_html(
            '<img src="{}" alt="{}" style="max-width:260px;width:100%;height:auto;border-radius:18px;border:1px solid #d9d9d9;">',
            obj.portrait.image.url,
            obj.portrait.alt or obj.portrait.title or obj.name,
        )

    @admin.display(description='Где вы сейчас')
    def structure_panel(self, obj):
        if not obj.pk:
            return 'Сначала сохраните героя, после этого появятся быстрые переходы по иерархии.'

        page_url = self._changelist_url('admin:heroes_heropage_changelist', hero__id__exact=obj.pk)
        section_url = self._changelist_url('admin:heroes_pagesection_changelist', page__hero__id__exact=obj.pk)
        block_url = self._changelist_url('admin:content_block_changelist', section__page__hero__id__exact=obj.pk)
        public_url = reverse('heroes:detail', args=[obj.slug])

        return format_html(
            '<div class="tmb-admin-panel">'
            '<div class="tmb-admin-path">Герой → страницы героя → секции страницы → блоки секции</div>'
            '<div class="tmb-admin-links">{}{}{}{}</div>'
            '</div>',
            self._button('Открыть страницы', page_url),
            self._button('Открыть секции', section_url),
            self._button('Открыть блоки', block_url),
            self._button('Открыть героя на сайте ↗', public_url, 'primary'),
        )


@admin.register(HeroPage)
class HeroPageAdmin(AdminUxMixin, admin.ModelAdmin):
    list_display = (
        'icon_thumb',
        'title',
        'navigation_label_preview',
        'hero_link',
        'structure_stats',
        'open_public_page',
        'order',
        'is_published',
    )
    list_display_links = ('title',)
    list_editable = ('order', 'is_published')
    search_fields = (
        'title',
        'code',
        'slug',
        'tab_label',
        'lead',
        'hero__name',
        'hero__slug',
        'icon__title',
        'icon__slug',
        'icon__alt',
    )
    search_help_text = 'Поиск по названию страницы, короткой подписи, герою и иконке.'
    list_filter = ('hero', 'is_published')
    ordering = ('hero__name', 'order', 'title')
    list_select_related = ('hero', 'icon')
    inlines = (PageSectionInline,)
    autocomplete_fields = ('hero', 'icon')
    readonly_fields = ('icon_preview', 'fallback_icon_badge', 'hierarchy_panel', 'navigation_preview')
    fieldsets = (
        (
            'Где находится страница',
            {
                'fields': (
                    'hero',
                    'hierarchy_panel',
                ),
            },
        ),
        (
            'Главное для редактора',
            {
                'fields': (
                    'title',
                    'tab_label',
                    'navigation_preview',
                    'lead',
                ),
                'description': 'Полное название страницы можно оставить редакторским. Для навигации используйте короткий tab_label.',
            },
        ),
        (
            'Маршрут и иконка',
            {
                'fields': (
                    'code',
                    'slug',
                    'icon',
                    'icon_preview',
                    'fallback_icon_badge',
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
    prepopulated_fields = {'slug': ('title',)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('hero', 'icon').annotate(
            section_total=Count('sections', distinct=True),
            block_total=Count('sections__blocks', distinct=True),
        )

    @admin.display(description='Иконка')
    def icon_thumb(self, obj):
        return format_html(
            '<img src="{}" alt="" style="width:32px;height:32px;object-fit:contain;border-radius:8px;border:1px solid #d9d9d9;background:#fff;padding:4px;">',
            obj.icon_url,
        )

    @admin.display(description='Как видно в навигации')
    def navigation_label_preview(self, obj):
        return obj.navigation_label

    @admin.display(description='Герой', ordering='hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.hero.name)

    @admin.display(description='Секции и блоки')
    def structure_stats(self, obj):
        return format_html(
            '<span class="tmb-admin-kpi">Секций: {}</span><span class="tmb-admin-kpi">Блоков: {}</span>',
            getattr(obj, 'section_total', 0),
            getattr(obj, 'block_total', 0),
        )

    @admin.display(description='Открыть на сайте')
    def open_public_page(self, obj):
        url = reverse('heroes:page_detail', args=[obj.hero.slug, obj.slug])
        return self._button('Страница ↗', url, 'primary')

    @admin.display(description='Fallback-иконка')
    def fallback_icon_badge(self, obj):
        return format_html('<span class="tmb-admin-kpi">{}</span>', obj.resolved_icon_key)

    @admin.display(description='Превью иконки')
    def icon_preview(self, obj):
        if not obj.pk:
            return 'Сначала сохраните страницу.'
        return format_html(
            '<img src="{}" alt="" style="width:52px;height:52px;object-fit:contain;border-radius:10px;border:1px solid #d9d9d9;background:#fff;padding:6px;">',
            obj.icon_url,
        )

    @admin.display(description='Иерархия и переходы')
    def hierarchy_panel(self, obj):
        if not obj.pk:
            return 'Сначала сохраните страницу, потом появятся ссылки на героя, секции и блоки.'

        hero_url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        sections_url = self._changelist_url('admin:heroes_pagesection_changelist', page__id__exact=obj.pk)
        blocks_url = self._changelist_url('admin:content_block_changelist', section__page__id__exact=obj.pk)
        public_url = reverse('heroes:page_detail', args=[obj.hero.slug, obj.slug])

        return format_html(
            '<div class="tmb-admin-panel">'
            '<div class="tmb-admin-path">{} / {}</div>'
            '<div class="tmb-admin-links">{}{}{}{}</div>'
            '</div>',
            obj.hero.name,
            obj.display_title,
            self._button('Открыть героя', hero_url),
            self._button('Открыть секции', sections_url),
            self._button('Открыть блоки', blocks_url),
            self._button('Открыть страницу на сайте ↗', public_url, 'primary'),
        )

    @admin.display(description='Как это увидит пользователь')
    def navigation_preview(self, obj):
        hero_name = obj.hero.name if obj.hero_id else 'Герой'
        public_label = obj.navigation_label if obj.pk else 'Подпись появится после сохранения'
        page_title = obj.display_title if obj.pk else 'Название страницы'
        return format_html(
            '<div class="tmb-admin-nav-preview">'
            '<div class="tmb-admin-nav-preview__hero">{}</div>'
            '<div class="tmb-admin-nav-preview__pages">'
            '<span class="tmb-admin-nav-pill tmb-admin-nav-pill--current">{}</span>'
            '</div>'
            '<div class="tmb-admin-nav-preview__note">Заголовок страницы: {}</div>'
            '</div>',
            hero_name,
            public_label,
            page_title,
        )


@admin.register(PageSection)
class PageSectionAdmin(AdminUxMixin, admin.ModelAdmin):
    list_display = (
        'title',
        'page_link',
        'hero_link',
        'block_count_badge',
        'open_public_section',
        'order',
        'is_published',
    )
    list_display_links = ('title',)
    list_editable = ('order', 'is_published')
    search_fields = (
        'title',
        'code',
        'slug',
        'description',
        'page__title',
        'page__tab_label',
        'page__hero__name',
    )
    search_help_text = 'Поиск по секции, странице и герою.'
    list_filter = ('is_published', 'page__hero', 'page')
    ordering = ('page__hero__name', 'page__order', 'order', 'title')
    autocomplete_fields = ('page',)
    readonly_fields = ('hierarchy_panel',)
    inlines = (BlockInline,)
    fieldsets = (
        (
            'Где находится секция',
            {
                'fields': (
                    'page',
                    'hierarchy_panel',
                ),
            },
        ),
        (
            'Содержимое секции',
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
            'Публикация и порядок',
            {
                'fields': (
                    'order',
                    'is_published',
                ),
            },
        ),
    )
    prepopulated_fields = {'slug': ('title',)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('page', 'page__hero').annotate(block_total=Count('blocks', distinct=True))

    @admin.display(description='Страница', ordering='page__title')
    def page_link(self, obj):
        url = reverse('admin:heroes_heropage_change', args=[obj.page_id])
        return format_html('<a href="{}">{}</a>', url, obj.page.display_title)

    @admin.display(description='Герой', ordering='page__hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.page.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.page.hero.name)

    @admin.display(description='Блоки')
    def block_count_badge(self, obj):
        url = self._changelist_url('admin:content_block_changelist', section__id__exact=obj.pk)
        return format_html('<a class="tmb-admin-kpi tmb-admin-kpi--link" href="{}">Блоков: {}</a>', url, getattr(obj, 'block_total', 0))

    @admin.display(description='Сайт')
    def open_public_section(self, obj):
        url = reverse('heroes:page_detail', args=[obj.page.hero.slug, obj.page.slug]) + f'#section-{obj.slug}'
        return self._button('Секция ↗', url, 'primary')

    @admin.display(description='Иерархия и переходы')
    def hierarchy_panel(self, obj):
        if not obj.pk:
            return 'Сначала сохраните секцию, потом появятся ссылки на страницу, героя и блоки.'

        hero_url = reverse('admin:heroes_hero_change', args=[obj.page.hero_id])
        page_url = reverse('admin:heroes_heropage_change', args=[obj.page_id])
        blocks_url = self._changelist_url('admin:content_block_changelist', section__id__exact=obj.pk)
        public_url = reverse('heroes:page_detail', args=[obj.page.hero.slug, obj.page.slug]) + f'#section-{obj.slug}'

        return format_html(
            '<div class="tmb-admin-panel">'
            '<div class="tmb-admin-path">{} / {} / {}</div>'
            '<div class="tmb-admin-links">{}{}{}{}</div>'
            '</div>',
            obj.page.hero.name,
            obj.page.display_title,
            obj.title,
            self._button('Открыть героя', hero_url),
            self._button('Открыть страницу', page_url),
            self._button('Открыть блоки', blocks_url),
            self._button('Открыть секцию на сайте ↗', public_url, 'primary'),
        )
