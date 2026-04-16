from django.contrib import admin

from .models import Hero, HeroPage, PageSection


class HeroPageInline(admin.TabularInline):
    model = HeroPage
    extra = 0
    fields = ('title', 'code', 'slug', 'tab_label', 'order', 'is_published')
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


admin.site.register(PageSection)
