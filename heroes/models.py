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
