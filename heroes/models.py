from django.db import models

from .page_icons import build_icon_static_path, resolve_page_icon_key, resolve_page_icon_url


class Hero(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    accent = models.CharField(max_length=32, blank=True)
    portrait = models.ForeignKey(
        'content.Asset',
        on_delete=models.SET_NULL,
        related_name='heroes',
        blank=True,
        null=True,
        limit_choices_to={'kind': 'hero-portrait'},
        verbose_name='Портрет',
    )
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ('order', 'name')

    def __str__(self) -> str:
        return self.name


class HeroPage(models.Model):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name='pages')
    code = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200)
    title = models.CharField(max_length=255)
    tab_label = models.CharField(max_length=255, blank=True)
    lead = models.TextField(blank=True)
    icon = models.ForeignKey(
        'content.Asset',
        on_delete=models.SET_NULL,
        related_name='hero_pages_with_icon',
        blank=True,
        null=True,
        limit_choices_to={'kind': 'page-icon'},
        verbose_name='Иконка страницы',
    )
    icon_key = models.CharField(
        max_length=32,
        blank=True,
        default='',
        verbose_name='Legacy fallback icon key',
    )
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ('hero', 'order', 'title')

    def __str__(self) -> str:
        return f'{self.hero.name} / {self.display_title}'

    @staticmethod
    def _strip_hero_prefix(title: str, hero_name: str) -> str:
        clean_title = str(title or '').strip()
        clean_hero_name = str(hero_name or '').strip()

        if not clean_title or not clean_hero_name:
            return clean_title

        if clean_title.casefold() == clean_hero_name.casefold():
            return clean_title

        if clean_title.casefold().startswith(clean_hero_name.casefold()):
            remainder = clean_title[len(clean_hero_name):].lstrip(' —–-:/|·•')
            if remainder:
                return remainder.strip()

        return clean_title

    @property
    def display_title(self) -> str:
        cleaned_title = self._strip_hero_prefix(self.title, self.hero.name)
        return cleaned_title or self.title

    @property
    def navigation_label(self) -> str:
        return str(self.tab_label or '').strip() or self.display_title

    @property
    def resolved_icon_key(self) -> str:
        return resolve_page_icon_key(self)

    @property
    def icon_static_path(self) -> str:
        return build_icon_static_path(self)

    @property
    def icon_url(self) -> str:
        return resolve_page_icon_url(self)


class PageSection(models.Model):
    page = models.ForeignKey(HeroPage, on_delete=models.CASCADE, related_name='sections')
    code = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ('page', 'order', 'title')

    def __str__(self) -> str:
        return f'{self.page.hero.name} / {self.page.display_title} / {self.title}'
