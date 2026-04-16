from django.db import models


class Hero(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    accent = models.CharField(max_length=32, blank=True)
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
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ('hero', 'order', 'title')

    def __str__(self) -> str:
        return f'{self.hero} — {self.title}'


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
        return f'{self.page} — {self.title}'
