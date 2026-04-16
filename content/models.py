from django.db import models


class Block(models.Model):
    section = models.ForeignKey(
        'heroes.PageSection',
        verbose_name='секция',
        on_delete=models.CASCADE,
        related_name='blocks',
    )
    type = models.CharField('тип блока', max_length=100)
    title = models.CharField('заголовок блока', max_length=255, blank=True, null=True)
    variant = models.CharField('вариант', max_length=100, blank=True, null=True)
    anchor = models.SlugField('якорь', max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField('порядок', default=0)
    schema_version = models.PositiveIntegerField('версия схемы', default=1)
    data = models.JSONField('данные JSON', default=dict, blank=True)
    is_published = models.BooleanField('опубликован', default=False)

    class Meta:
        ordering = ('section', 'order', 'id')
        verbose_name = 'блок'
        verbose_name_plural = 'блоки'

    def __str__(self) -> str:
        label = self.title or self.type
        return f'{self.section} — {label}'
