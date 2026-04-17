from urllib.parse import urlencode

from django.contrib import admin
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html

from .models import Hero, HeroPage, PageSection


admin.site.site_header = 'Too Many Bones Helper — редакторская панель'
admin.site.site_title = 'TMB Admin'
admin.site.index_title = 'Герои, контент и игровые данные'

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


class HiddenFromIndexAdminMixin:
    def get_model_perms(self, request):
        return {}


class HeroPageInline(admin.TabularInline):
    model = HeroPage
    extra = 0
    fields = ('title', 'tab_label_preview', 'order', 'is_published', 'open_in_content')
    ordering = ('order', 'title')
    readonly_fields = ('tab_label_preview', 'open_in_content')
    show_change_link = False
    verbose_name = 'Страница героя'
    verbose_name_plural = 'Страницы героя'

    @admin.display(description='Навигация')
    def tab_label_preview(self, obj):
        if not obj.pk:
            return 'Сначала сохраните страницу.'
        return str(obj.tab_label or '').strip() or obj.title

    @admin.display(description='Редактирование')
    def open_in_content(self, obj):
        if not obj.pk:
            return '—'
        url = reverse('admin:content_contentheropage_change', args=[obj.pk])
        return format_html('<a href="{}">Открыть в контенте</a>', url)


@admin.register(Hero)
class HeroAdmin(AdminUxMixin, admin.ModelAdmin):
    list_display = (
        'portrait_thumb',
        'name',
        'content_stats',
        'game_stats',
        'open_content_pages',
        'open_game_layer',
        'order',
        'is_published',
    )
    list_editable = ('order', 'is_published')
    list_display_links = ('name',)
    search_fields = ('name', 'slug', 'tagline', 'description', 'accent', 'portrait__title', 'portrait__slug')
    search_help_text = 'Поиск по герою, описанию и портрету.'
    list_filter = ('is_published',)
    ordering = ('order', 'name')
    list_select_related = ('portrait',)
    autocomplete_fields = ('portrait',)
    readonly_fields = ('portrait_preview', 'structure_panel')
    inlines = (HeroPageInline,)
    fieldsets = (
        ('Главное', {'fields': ('name', 'slug', 'structure_panel')}),
        ('Визуальный образ героя', {'fields': ('portrait', 'portrait_preview', 'accent')}),
        ('Коротко о герое', {'fields': ('tagline', 'description')}),
        ('Публикация и порядок', {'fields': ('order', 'is_published')}),
    )
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('portrait').annotate(
            page_total=Count('pages', distinct=True),
            section_total=Count('pages__sections', distinct=True),
            block_total=Count('pages__sections__blocks', distinct=True),
            way_total=Count('ways', distinct=True),
            die_total=Count('dice', distinct=True),
            supply_total=Count('supplies', distinct=True),
            backup_plan_total=Count('backup_plan_skills', distinct=True),
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

    @admin.display(description='Контент')
    def content_stats(self, obj):
        return format_html(
            '<span class="tmb-admin-kpi">Страниц: {}</span>'
            '<span class="tmb-admin-kpi">Секций: {}</span>'
            '<span class="tmb-admin-kpi">Блоков: {}</span>',
            getattr(obj, 'page_total', 0),
            getattr(obj, 'section_total', 0),
            getattr(obj, 'block_total', 0),
        )

    @admin.display(description='Игровые данные')
    def game_stats(self, obj):
        return format_html(
            '<span class="tmb-admin-kpi">Путей: {}</span>'
            '<span class="tmb-admin-kpi">Кубиков: {}</span>'
            '<span class="tmb-admin-kpi">BP: {}</span>'
            '<span class="tmb-admin-kpi">Запасов: {}</span>',
            getattr(obj, 'way_total', 0),
            getattr(obj, 'die_total', 0),
            getattr(obj, 'backup_plan_total', 0),
            getattr(obj, 'supply_total', 0),
        )

    @admin.display(description='Контент героя')
    def open_content_pages(self, obj):
        url = self._changelist_url('admin:content_contentheropage_changelist', hero__id__exact=obj.pk)
        return self._button('Открыть контент', url)

    @admin.display(description='Игровой слой')
    def open_game_layer(self, obj):
        url = self._changelist_url('admin:game_way_changelist', hero__id__exact=obj.pk)
        return self._button('Открыть игровые данные', url)

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
            return 'Сначала сохраните героя, после этого появятся быстрые переходы к контенту и игровым сущностям.'

        pages_url = self._changelist_url('admin:content_contentheropage_changelist', hero__id__exact=obj.pk)
        sections_url = self._changelist_url('admin:content_contentpagesection_changelist', page__hero__id__exact=obj.pk)
        blocks_url = self._changelist_url('admin:content_block_changelist', section__page__hero__id__exact=obj.pk)
        ways_url = self._changelist_url('admin:game_way_changelist', hero__id__exact=obj.pk)
        dice_url = self._changelist_url('admin:game_die_changelist', hero__id__exact=obj.pk)
        backup_url = self._changelist_url('admin:game_backupplanskill_changelist', hero__id__exact=obj.pk)
        supply_url = self._changelist_url('admin:game_supply_changelist', hero__id__exact=obj.pk)
        public_url = reverse('heroes:detail', args=[obj.slug])

        return format_html(
            '<div class="tmb-admin-panel">'
            '<div class="tmb-admin-path">Первый выбор — герой. Внутри героя есть два слоя: контент и игровые данные.</div>'
            '<div class="tmb-admin-links">{}{}</div>'
            '<div class="tmb-admin-links">{}{}{}</div>'
            '<div class="tmb-admin-links">{}{}{}</div>'
            '</div>',
            self._button('Страницы героя', pages_url),
            self._button('Секции страницы', sections_url),
            self._button('Блоки секций', blocks_url),
            self._button('Пути героя', ways_url),
            self._button('Кубики героя', dice_url),
            self._button('Навыки BP', backup_url),
            self._button('Запасы героя', supply_url),
            self._button('Открыть героя на сайте ↗', public_url, 'primary'),
        )


@admin.register(HeroPage)
class HiddenHeroPageAdmin(HiddenFromIndexAdminMixin, AdminUxMixin, admin.ModelAdmin):
    search_fields = ('title', 'tab_label', 'code', 'slug', 'hero__name')
    list_select_related = ('hero', 'icon')
    autocomplete_fields = ('hero', 'icon')
    ordering = ('hero__name', 'order', 'title')


@admin.register(PageSection)
class HiddenPageSectionAdmin(HiddenFromIndexAdminMixin, AdminUxMixin, admin.ModelAdmin):
    search_fields = ('title', 'code', 'slug', 'page__title', 'page__hero__name')
    list_select_related = ('page', 'page__hero')
    autocomplete_fields = ('page',)
    ordering = ('page__hero__name', 'page__order', 'order', 'title')
