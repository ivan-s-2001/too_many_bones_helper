from django.db import models


class Hero(models.Model):
    slug = models.SlugField('slug', max_length=200, unique=True)
    name = models.CharField('имя героя', max_length=255)
    tagline = models.CharField('краткий слоган', max_length=255, blank=True)
    description = models.TextField('описание', blank=True)
    accent = models.CharField('акцент', max_length=32, blank=True)
    order = models.PositiveIntegerField('порядок', default=0)
    is_published = models.BooleanField('опубликован', default=False)

    class Meta:
        ordering = ('order', 'name')
        verbose_name = 'герой'
        verbose_name_plural = 'герои'

    def __str__(self) -> str:
        return self.name


class HeroPage(models.Model):
    hero = models.ForeignKey(
        Hero,
        verbose_name='герой',
        on_delete=models.CASCADE,
        related_name='pages',
    )
    code = models.CharField('код страницы', max_length=100)
    slug = models.SlugField('slug страницы', max_length=200)
    title = models.CharField('заголовок страницы', max_length=255)
    tab_label = models.CharField('подпись вкладки', max_length=255, blank=True)
    lead = models.TextField('вводный текст', blank=True)
    order = models.PositiveIntegerField('порядок', default=0)
    is_published = models.BooleanField('опубликована', default=False)

    class Meta:
        ordering = ('hero', 'order', 'title')
        verbose_name = 'страница героя'
        verbose_name_plural = 'страницы героя'

    def __str__(self) -> str:
        return f'{self.hero} — {self.title}'


class PageSection(models.Model):
    page = models.ForeignKey(
        HeroPage,
        verbose_name='страница героя',
        on_delete=models.CASCADE,
        related_name='sections',
    )
    code = models.CharField('код секции', max_length=100)
    slug = models.SlugField('slug секции', max_length=200)
    title = models.CharField('заголовок секции', max_length=255)
    description = models.TextField('описание секции', blank=True)
    order = models.PositiveIntegerField('порядок', default=0)
    is_published = models.BooleanField('опубликована', default=False)

    class Meta:
        ordering = ('page', 'order', 'title')
        verbose_name = 'секция страницы'
        verbose_name_plural = 'секции страницы'

    def __str__(self) -> str:
        return f'{self.page} — {self.title}'
