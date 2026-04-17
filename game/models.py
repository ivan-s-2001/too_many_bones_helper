from django.db import models


class Way(models.Model):
    hero = models.ForeignKey(
        'heroes.Hero',
        on_delete=models.CASCADE,
        related_name='ways',
        verbose_name='Герой',
    )
    code = models.CharField('Код', max_length=100)
    slug = models.SlugField('Слаг', max_length=200)
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубликовано', default=False)

    class Meta:
        ordering = ('hero', 'order', 'title')
        verbose_name = 'Путь'
        verbose_name_plural = 'Пути'
        constraints = [
            models.UniqueConstraint(fields=('hero', 'code'), name='game_way_unique_hero_code'),
            models.UniqueConstraint(fields=('hero', 'slug'), name='game_way_unique_hero_slug'),
        ]

    def __str__(self) -> str:
        return f'{self.hero} — {self.title}'


class Die(models.Model):
    hero = models.ForeignKey(
        'heroes.Hero',
        on_delete=models.CASCADE,
        related_name='dice',
        verbose_name='Герой',
    )
    way = models.ForeignKey(
        Way,
        on_delete=models.SET_NULL,
        related_name='dice',
        blank=True,
        null=True,
        verbose_name='Путь',
    )
    code = models.CharField('Код', max_length=100)
    title = models.CharField('Название', max_length=255)
    kind = models.CharField('Тип', max_length=100, blank=True)
    description = models.TextField('Описание', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубликовано', default=False)

    class Meta:
        ordering = ('hero', 'order', 'title')
        verbose_name = 'Кубик'
        verbose_name_plural = 'Кубики'
        constraints = [
            models.UniqueConstraint(fields=('hero', 'code'), name='game_die_unique_hero_code'),
        ]

    def __str__(self) -> str:
        return f'{self.hero} — {self.title}'


class DieFace(models.Model):
    die = models.ForeignKey(
        Die,
        on_delete=models.CASCADE,
        related_name='faces',
        verbose_name='Кубик',
    )
    face_index = models.PositiveSmallIntegerField('Номер грани')
    title = models.CharField('Название', max_length=255, blank=True)
    description = models.TextField('Описание', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ('die', 'face_index', 'order', 'id')
        verbose_name = 'Грань кубика'
        verbose_name_plural = 'Грани кубиков'
        constraints = [
            models.UniqueConstraint(fields=('die', 'face_index'), name='game_die_face_unique_index'),
        ]

    def __str__(self) -> str:
        label = self.title or f'Грань {self.face_index}'
        return f'{self.die} — {label}'


class BackupPlanSkill(models.Model):
    hero = models.ForeignKey(
        'heroes.Hero',
        on_delete=models.CASCADE,
        related_name='backup_plan_skills',
        verbose_name='Герой',
    )
    level = models.PositiveIntegerField('Уровень')
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубликовано', default=False)

    class Meta:
        ordering = ('hero', 'level', 'order', 'title')
        verbose_name = 'Навык запасного плана'
        verbose_name_plural = 'Навыки запасного плана'
        constraints = [
            models.UniqueConstraint(fields=('hero', 'level'), name='game_backup_plan_unique_level'),
        ]

    def __str__(self) -> str:
        return f'{self.hero} — {self.level} BP — {self.title}'


class Supply(models.Model):
    hero = models.ForeignKey(
        'heroes.Hero',
        on_delete=models.CASCADE,
        related_name='supplies',
        verbose_name='Герой',
    )
    code = models.CharField('Код', max_length=100)
    slug = models.SlugField('Слаг', max_length=200)
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубликовано', default=False)

    class Meta:
        ordering = ('hero', 'order', 'title')
        verbose_name = 'Запас'
        verbose_name_plural = 'Запасы'
        constraints = [
            models.UniqueConstraint(fields=('hero', 'code'), name='game_supply_unique_hero_code'),
            models.UniqueConstraint(fields=('hero', 'slug'), name='game_supply_unique_hero_slug'),
        ]

    def __str__(self) -> str:
        return f'{self.hero} — {self.title}'
