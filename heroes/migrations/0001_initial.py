from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Hero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('tagline', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('accent', models.CharField(blank=True, max_length=32)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_published', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('order', 'name'),
            },
        ),
    ]
