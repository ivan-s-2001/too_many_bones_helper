from urllib.parse import urlencode

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from .models import BackupPlanSkill, Die, DieFace, Supply, Way


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


@admin.register(Way)
class WayAdmin(AdminUxMixin, admin.ModelAdmin):
    list_display = ('title', 'hero_link', 'dice_count', 'order', 'is_published')
    list_display_links = ('title',)
    list_editable = ('order', 'is_published')
    search_fields = ('title', 'code', 'slug', 'description', 'hero__name')
    list_filter = ('is_published', 'hero')
    ordering = ('hero__name', 'order', 'title')
    autocomplete_fields = ('hero',)
    readonly_fields = ('hierarchy_panel',)
    fieldsets = (
        ('Где находится путь', {'fields': ('hero', 'hierarchy_panel')}),
        ('Основное', {'fields': ('title', 'code', 'slug', 'description')}),
        ('Публикация и порядок', {'fields': ('order', 'is_published')}),
    )
    prepopulated_fields = {'slug': ('title',)}

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('hero').annotate(dice_total=Count('dice', distinct=True))

    @admin.display(description='Герой', ordering='hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.hero.name)

    @admin.display(description='Кубики')
    def dice_count(self, obj):
        url = self._changelist_url('admin:game_die_changelist', way__id__exact=obj.pk)
        return format_html('<a class="tmb-admin-kpi tmb-admin-kpi--link" href="{}">Кубиков: {}</a>', url, getattr(obj, 'dice_total', 0))

    @admin.display(description='Иерархия и переходы')
    def hierarchy_panel(self, obj):
        if not obj.pk:
            return 'Сначала сохраните путь, потом появятся ссылки на героя и кубики.'
        hero_url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        dice_url = self._changelist_url('admin:game_die_changelist', way__id__exact=obj.pk)
        return format_html(
            '<div class="tmb-admin-panel"><div class="tmb-admin-path">{} / Путь / {}</div><div class="tmb-admin-links">{}{}</div></div>',
            obj.hero.name,
            obj.title,
            self._button('Открыть героя', hero_url),
            self._button('Открыть кубики пути', dice_url),
        )


@admin.register(Die)
class DieAdmin(AdminUxMixin, admin.ModelAdmin):
    list_display = ('title', 'kind', 'hero_link', 'way_link', 'faces_count', 'order', 'is_published')
    list_display_links = ('title',)
    list_editable = ('order', 'is_published')
    search_fields = ('title', 'code', 'kind', 'description', 'hero__name', 'way__title')
    list_filter = ('is_published', 'hero', 'way', 'kind')
    ordering = ('hero__name', 'order', 'title')
    autocomplete_fields = ('hero', 'way')
    readonly_fields = ('hierarchy_panel',)
    fieldsets = (
        ('Где находится кубик', {'fields': ('hero', 'way', 'hierarchy_panel')}),
        ('Основное', {'fields': ('title', 'code', 'kind', 'description')}),
        ('Публикация и порядок', {'fields': ('order', 'is_published')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('hero', 'way').annotate(face_total=Count('faces', distinct=True))

    @admin.display(description='Герой', ordering='hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.hero.name)

    @admin.display(description='Путь', ordering='way__title')
    def way_link(self, obj):
        if not obj.way_id:
            return '—'
        url = reverse('admin:game_way_change', args=[obj.way_id])
        return format_html('<a href="{}">{}</a>', url, obj.way.title)

    @admin.display(description='Грани')
    def faces_count(self, obj):
        url = self._changelist_url('admin:game_dieface_changelist', die__id__exact=obj.pk)
        return format_html('<a class="tmb-admin-kpi tmb-admin-kpi--link" href="{}">Граней: {}</a>', url, getattr(obj, 'face_total', 0))

    @admin.display(description='Иерархия и переходы')
    def hierarchy_panel(self, obj):
        if not obj.pk:
            return 'Сначала сохраните кубик, потом появятся ссылки на героя, путь и грани.'
        hero_url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        way_button = '' if not obj.way_id else self._button('Открыть путь', reverse('admin:game_way_change', args=[obj.way_id]))
        faces_url = self._changelist_url('admin:game_dieface_changelist', die__id__exact=obj.pk)
        return format_html(
            '<div class="tmb-admin-panel"><div class="tmb-admin-path">{} / Кубик / {}</div><div class="tmb-admin-links">{}{}{}</div></div>',
            obj.hero.name,
            obj.title,
            self._button('Открыть героя', hero_url),
            way_button,
            self._button('Открыть грани', faces_url),
        )


@admin.register(DieFace)
class DieFaceAdmin(AdminUxMixin, admin.ModelAdmin):
    list_display = ('face_label', 'die_link', 'hero_link', 'face_index', 'order')
    list_display_links = ('face_label',)
    list_editable = ('order',)
    search_fields = ('title', 'description', 'die__title', 'die__hero__name')
    list_filter = ('die__hero', 'die')
    ordering = ('die__hero__name', 'die__title', 'face_index', 'order')
    autocomplete_fields = ('die',)
    readonly_fields = ('hierarchy_panel',)
    fieldsets = (
        ('Где находится грань', {'fields': ('die', 'hierarchy_panel')}),
        ('Основное', {'fields': ('face_index', 'title', 'description')}),
        ('Порядок', {'fields': ('order',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('die', 'die__hero')

    @admin.display(description='Грань', ordering='title')
    def face_label(self, obj):
        return obj.title or f'Грань {obj.face_index}'

    @admin.display(description='Кубик', ordering='die__title')
    def die_link(self, obj):
        url = reverse('admin:game_die_change', args=[obj.die_id])
        return format_html('<a href="{}">{}</a>', url, obj.die.title)

    @admin.display(description='Герой', ordering='die__hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.die.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.die.hero.name)

    @admin.display(description='Иерархия и переходы')
    def hierarchy_panel(self, obj):
        if not obj.pk:
            return 'Сначала сохраните грань, потом появятся ссылки на героя и кубик.'
        hero_url = reverse('admin:heroes_hero_change', args=[obj.die.hero_id])
        die_url = reverse('admin:game_die_change', args=[obj.die_id])
        return format_html(
            '<div class="tmb-admin-panel"><div class="tmb-admin-path">{} / Кубик / {} / Грань {}</div><div class="tmb-admin-links">{}{}</div></div>',
            obj.die.hero.name,
            obj.die.title,
            obj.face_index,
            self._button('Открыть героя', hero_url),
            self._button('Открыть кубик', die_url),
        )


@admin.register(BackupPlanSkill)
class BackupPlanSkillAdmin(AdminUxMixin, admin.ModelAdmin):
    list_display = ('title', 'hero_link', 'level', 'order', 'is_published')
    list_display_links = ('title',)
    list_editable = ('order', 'is_published')
    search_fields = ('title', 'description', 'hero__name')
    list_filter = ('is_published', 'hero')
    ordering = ('hero__name', 'level', 'order', 'title')
    autocomplete_fields = ('hero',)
    readonly_fields = ('hierarchy_panel',)
    fieldsets = (
        ('Где находится навык', {'fields': ('hero', 'hierarchy_panel')}),
        ('Основное', {'fields': ('level', 'title', 'description')}),
        ('Публикация и порядок', {'fields': ('order', 'is_published')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('hero')

    @admin.display(description='Герой', ordering='hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.hero.name)

    @admin.display(description='Иерархия и переходы')
    def hierarchy_panel(self, obj):
        if not obj.pk:
            return 'Сначала сохраните навык запасного плана, потом появится ссылка на героя.'
        hero_url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        return format_html(
            '<div class="tmb-admin-panel"><div class="tmb-admin-path">{} / Запасной план / {} BP / {}</div><div class="tmb-admin-links">{}</div></div>',
            obj.hero.name,
            obj.level,
            obj.title,
            self._button('Открыть героя', hero_url),
        )


@admin.register(Supply)
class SupplyAdmin(AdminUxMixin, admin.ModelAdmin):
    list_display = ('title', 'hero_link', 'code', 'order', 'is_published')
    list_display_links = ('title',)
    list_editable = ('order', 'is_published')
    search_fields = ('title', 'code', 'slug', 'description', 'hero__name')
    list_filter = ('is_published', 'hero')
    ordering = ('hero__name', 'order', 'title')
    autocomplete_fields = ('hero',)
    readonly_fields = ('hierarchy_panel',)
    fieldsets = (
        ('Где находится запас', {'fields': ('hero', 'hierarchy_panel')}),
        ('Основное', {'fields': ('title', 'code', 'slug', 'description')}),
        ('Публикация и порядок', {'fields': ('order', 'is_published')}),
    )
    prepopulated_fields = {'slug': ('title',)}

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('hero')

    @admin.display(description='Герой', ordering='hero__name')
    def hero_link(self, obj):
        url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        return format_html('<a href="{}">{}</a>', url, obj.hero.name)

    @admin.display(description='Иерархия и переходы')
    def hierarchy_panel(self, obj):
        if not obj.pk:
            return 'Сначала сохраните запас, потом появится ссылка на героя.'
        hero_url = reverse('admin:heroes_hero_change', args=[obj.hero_id])
        return format_html(
            '<div class="tmb-admin-panel"><div class="tmb-admin-path">{} / Запасы / {}</div><div class="tmb-admin-links">{}</div></div>',
            obj.hero.name,
            obj.title,
            self._button('Открыть героя', hero_url),
        )
