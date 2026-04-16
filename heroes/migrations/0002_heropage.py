from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('heroes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=200)),
                ('title', models.CharField(max_length=255)),
                ('tab_label', models.CharField(blank=True, max_length=255)),
                ('lead', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_published', models.BooleanField(default=False)),
                ('hero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='heroes.hero')),
            ],
            options={
                'ordering': ('hero', 'order', 'title'),
            },
        ),
    ]
