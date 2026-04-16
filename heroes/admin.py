from django.contrib import admin

from .models import Hero, HeroPage, PageSection


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'accent', 'order', 'is_published')
    search_fields = ('name', 'slug', 'tagline', 'description', 'accent')
    list_filter = ('is_published',)
    ordering = ('order', 'name')


admin.site.register(HeroPage)
admin.site.register(PageSection)
