from pathlib import Path

from django.db import models
from django.utils.text import slugify

from heroes.models import HeroPage, PageSection


def asset_image_upload_to(instance, filename: str) -> str:
    extension = Path(filename).suffix.lower() or '.bin'
    kind = slugify(instance.kind or 'asset') or 'asset'
    slug = slugify(instance.slug or Path(filename).stem) or 'asset'
    return f'assets/{kind}/{slug}/{slug}{extension}'


class Asset(models.Model):
    class Kind(models.TextChoices):
        GENERIC = 'generic', 'Изображение'
        HERO_PORTRAIT = 'hero-portrait', 'Портрет героя'
        PAGE_ICON = 'page-icon', 'Иконка страницы'

    slug = models.SlugField('Слаг', max_length=200, unique=True)
    title = models.CharField('Название', max_length=255)
    kind = models.CharField(
        'Тип',
        max_length=50,
        choices=Kind.choices,
        default=Kind.GENERIC,
    )
    image = models.ImageField(
        'Файл изображения',
        upload_to=asset_image_upload_to,
        width_field='width',
        height_field='height',
    )
    alt = models.CharField('Alt-текст', max_length=255, blank=True)
    width = models.PositiveIntegerField('Ширина', blank=True, null=True, editable=False)
    height = models.PositiveIntegerField('Высота', blank=True, null=True, editable=False)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубликовано', default=False)

    class Meta:
        ordering = ('kind', 'order', 'title')
        verbose_name = 'Ассет'
        verbose_name_plural = 'Ассеты'

    def __str__(self) -> str:
        return self.title


class GenericAsset(Asset):
    class Meta:
        proxy = True
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class HeroPortraitAsset(Asset):
    class Meta:
        proxy = True
        verbose_name = 'Портрет героя'
        verbose_name_plural = 'Портреты героев'


class PageIconAsset(Asset):
    class Meta:
        proxy = True
        verbose_name = 'Иконка страницы'
        verbose_name_plural = 'Иконки страниц'


class ContentHeroPage(HeroPage):
    class Meta:
        proxy = True
        verbose_name = 'Страница героя'
        verbose_name_plural = 'Страницы героев'


class ContentPageSection(PageSection):
    class Meta:
        proxy = True
        verbose_name = 'Секция страницы'
        verbose_name_plural = 'Секции страниц'


class Block(models.Model):
    section = models.ForeignKey(
        'heroes.PageSection',
        on_delete=models.CASCADE,
        related_name='blocks',
    )
    type = models.CharField(max_length=100)
    title = models.CharField(max_length=255, blank=True, null=True)
    variant = models.CharField(max_length=100, blank=True, null=True)
    anchor = models.SlugField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    schema_version = models.PositiveIntegerField(default=1)
    data = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ('section', 'order', 'id')
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'

    def __str__(self) -> str:
        label = self.title or self.type
        return f'{self.section} — {label}'
