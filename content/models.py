from django.db import models


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

    def __str__(self) -> str:
        label = self.title or self.type
        return f'{self.section} — {label}'
