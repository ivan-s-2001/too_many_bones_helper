from django.core.management.base import BaseCommand, CommandError

from content.models import Block
from heroes.models import PageSection


DEMO_BLOCKS = [
    {
        'type': 'text',
        'title': 'Кто это такой',
        'anchor': 'demo-text',
        'data': {
            'text': (
                'Пикет — герой, который умеет гибко переключаться между режимами защиты и атаки.\n\n'
                'Этот демо-блок нужен, чтобы проверить человеческий редактор текстового типа и рендер нескольких абзацев.'
            ),
        },
    },
    {
        'type': 'list',
        'title': 'Что стоит помнить',
        'anchor': 'demo-list',
        'data': {
            'intro': 'Короткий список для проверки редактора list.',
            'items': [
                'Нужно следить за позиционированием.',
                'Важно понимать роль в команде.',
                'Не все билды одинаково хороши в соло и в пати.',
            ],
        },
    },
    {
        'type': 'fact',
        'title': 'Ключевой факт',
        'anchor': 'demo-fact',
        'data': {
            'value': '3+',
            'label': 'Оптимальный стартовый темп',
            'description': 'Условный пример, который позволяет проверить крупное значение, подпись и пояснение.',
        },
    },
    {
        'type': 'accent',
        'title': 'Главная мысль',
        'anchor': 'demo-accent',
        'data': {
            'badge': 'Важно',
            'text': 'Не пытайтесь превращать каждый блок в универсальный конструктор — здесь нужен простой редакторский UX.',
            'note': 'Этот блок показывает, как выглядит выделенное акцентное сообщение.',
        },
    },
    {
        'type': 'cards',
        'title': 'Сильные стороны',
        'anchor': 'demo-cards',
        'data': {
            'intro': 'Набор карточек для проверки сетки и удобного ввода.',
            'items': [
                {
                    'title': 'Гибкость',
                    'text': 'Можно быстро менять акценты под сценарий партии.',
                },
                {
                    'title': 'Надёжность',
                    'text': 'Даже простой набор решений остаётся полезным в большинстве боёв.',
                },
                {
                    'title': 'Порог входа',
                    'text': 'Нужно время, чтобы понять, что именно стоит усиливать в первую очередь.',
                },
            ],
        },
    },
    {
        'type': 'checklist',
        'title': 'Что проверить перед боем',
        'anchor': 'demo-checklist',
        'data': {
            'intro': 'Демо-чеклист для проверки пунктов с состояниями.',
            'items': [
                {'text': 'Выбрать текущую роль героя', 'checked': True},
                {'text': 'Проверить ключевые кубики', 'checked': True},
                {'text': 'Уточнить приоритет первой цели', 'checked': False},
            ],
        },
    },
]


class Command(BaseCommand):
    help = 'Добавляет или обновляет демонстрационные блоки для проверки block editor поверх уже загруженного тестового дампа.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--include-unpublished',
            action='store_true',
            help='Искать секции не только среди опубликованных записей.',
        )

    def handle(self, *args, **options):
        sections_queryset = PageSection.objects.select_related('page', 'page__hero').order_by(
            'page__hero__order',
            'page__order',
            'order',
            'id',
        )

        if not options['include_unpublished']:
            sections_queryset = sections_queryset.filter(
                is_published=True,
                page__is_published=True,
                page__hero__is_published=True,
            )

        sections = list(sections_queryset)
        if not sections:
            raise CommandError(
                'Не найдено подходящих секций. Сначала загрузите тестовый дамп с героями, страницами и секциями.'
            )

        for index, payload in enumerate(DEMO_BLOCKS):
            section = sections[index % len(sections)]
            block, created = Block.objects.update_or_create(
                section=section,
                anchor=payload['anchor'],
                defaults={
                    'type': payload['type'],
                    'title': payload['title'],
                    'variant': '',
                    'order': 100 + index,
                    'schema_version': 1,
                    'data': payload['data'],
                    'is_published': True,
                },
            )
            action = 'Создан' if created else 'Обновлён'
            self.stdout.write(
                self.style.SUCCESS(
                    f'{action}: {payload["type"]} -> {section.page.hero.name} / {section.page.title} / {section.title}'
                )
            )

        self.stdout.write(self.style.SUCCESS('Демо-блоки для проверки редактора готовы.'))
