from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_asset'),
        ('heroes', '0003_pagesection'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentHeroPage',
            fields=[],
            options={
                'verbose_name': 'Страница героя',
                'verbose_name_plural': 'Страницы героев',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('heroes.heropage',),
        ),
        migrations.CreateModel(
            name='ContentPageSection',
            fields=[],
            options={
                'verbose_name': 'Секция страницы',
                'verbose_name_plural': 'Секции страниц',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('heroes.pagesection',),
        ),
        migrations.CreateModel(
            name='GenericAsset',
            fields=[],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('content.asset',),
        ),
        migrations.CreateModel(
            name='HeroPortraitAsset',
            fields=[],
            options={
                'verbose_name': 'Портрет героя',
                'verbose_name_plural': 'Портреты героев',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('content.asset',),
        ),
        migrations.CreateModel(
            name='PageIconAsset',
            fields=[],
            options={
                'verbose_name': 'Иконка страницы',
                'verbose_name_plural': 'Иконки страниц',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('content.asset',),
        ),
    ]
