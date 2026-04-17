from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('heroes', '0004_hero_portrait'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackupPlanSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveIntegerField(verbose_name='Уровень')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_published', models.BooleanField(default=False, verbose_name='Опубликовано')),
                ('hero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='backup_plan_skills', to='heroes.hero', verbose_name='Герой')),
            ],
            options={
                'verbose_name': 'Навык запасного плана',
                'verbose_name_plural': 'Навыки запасного плана',
                'ordering': ('hero', 'level', 'order', 'title'),
                'constraints': [models.UniqueConstraint(fields=('hero', 'level'), name='game_backup_plan_unique_level')],
            },
        ),
        migrations.CreateModel(
            name='Supply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, verbose_name='Код')),
                ('slug', models.SlugField(max_length=200, verbose_name='Слаг')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_published', models.BooleanField(default=False, verbose_name='Опубликовано')),
                ('hero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplies', to='heroes.hero', verbose_name='Герой')),
            ],
            options={
                'verbose_name': 'Запас',
                'verbose_name_plural': 'Запасы',
                'ordering': ('hero', 'order', 'title'),
                'constraints': [
                    models.UniqueConstraint(fields=('hero', 'code'), name='game_supply_unique_hero_code'),
                    models.UniqueConstraint(fields=('hero', 'slug'), name='game_supply_unique_hero_slug'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Way',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, verbose_name='Код')),
                ('slug', models.SlugField(max_length=200, verbose_name='Слаг')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_published', models.BooleanField(default=False, verbose_name='Опубликовано')),
                ('hero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ways', to='heroes.hero', verbose_name='Герой')),
            ],
            options={
                'verbose_name': 'Путь',
                'verbose_name_plural': 'Пути',
                'ordering': ('hero', 'order', 'title'),
                'constraints': [
                    models.UniqueConstraint(fields=('hero', 'code'), name='game_way_unique_hero_code'),
                    models.UniqueConstraint(fields=('hero', 'slug'), name='game_way_unique_hero_slug'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Die',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, verbose_name='Код')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('kind', models.CharField(blank=True, max_length=100, verbose_name='Тип')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_published', models.BooleanField(default=False, verbose_name='Опубликовано')),
                ('hero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dice', to='heroes.hero', verbose_name='Герой')),
                ('way', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dice', to='game.way', verbose_name='Путь')),
            ],
            options={
                'verbose_name': 'Кубик',
                'verbose_name_plural': 'Кубики',
                'ordering': ('hero', 'order', 'title'),
                'constraints': [models.UniqueConstraint(fields=('hero', 'code'), name='game_die_unique_hero_code')],
            },
        ),
        migrations.CreateModel(
            name='DieFace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('face_index', models.PositiveSmallIntegerField(verbose_name='Номер грани')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('die', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faces', to='game.die', verbose_name='Кубик')),
            ],
            options={
                'verbose_name': 'Грань кубика',
                'verbose_name_plural': 'Грани кубиков',
                'ordering': ('die', 'face_index', 'order', 'id'),
                'constraints': [models.UniqueConstraint(fields=('die', 'face_index'), name='game_die_face_unique_index')],
            },
        ),
    ]
