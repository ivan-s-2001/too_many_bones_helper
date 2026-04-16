from django.templatetags.static import static
from django.utils.text import slugify


DEFAULT_ICON_KEY = 'default'
ICON_STATIC_PREFIX = 'heroes/page-icons'

BUILTIN_ICON_DEFINITIONS = [
    {
        'key': 'overview',
        'title': 'Overview / Main',
        'alt': 'Иконка страницы Overview / Main',
        'order': 10,
        'image': 'assets/page-icon/overview/overview.png',
    },
    {
        'key': 'start',
        'title': 'Start',
        'alt': 'Иконка страницы Start',
        'order': 20,
        'image': 'assets/page-icon/start/start.png',
    },
    {
        'key': 'progression',
        'title': 'Progression / Build',
        'alt': 'Иконка страницы Progression / Build',
        'order': 30,
        'image': 'assets/page-icon/progression/progression.png',
    },
    {
        'key': 'reference',
        'title': 'Reference',
        'alt': 'Иконка страницы Reference',
        'order': 40,
        'image': 'assets/page-icon/reference/reference.png',
    },
    {
        'key': 'tips',
        'title': 'Tips',
        'alt': 'Иконка страницы Tips',
        'order': 50,
        'image': 'assets/page-icon/tips/tips.png',
    },
    {
        'key': 'mistakes',
        'title': 'Mistakes',
        'alt': 'Иконка страницы Mistakes',
        'order': 60,
        'image': 'assets/page-icon/mistakes/mistakes.png',
    },
    {
        'key': 'tactics',
        'title': 'Tactics / Strategy',
        'alt': 'Иконка страницы Tactics / Strategy',
        'order': 70,
        'image': 'assets/page-icon/tactics/tactics.png',
    },
    {
        'key': 'traits',
        'title': 'Traits / Skills',
        'alt': 'Иконка страницы Traits / Skills',
        'order': 80,
        'image': 'assets/page-icon/traits/traits.png',
    },
    {
        'key': 'dice',
        'title': 'Dice',
        'alt': 'Иконка страницы Dice',
        'order': 90,
        'image': 'assets/page-icon/dice/dice.png',
    },
    {
        'key': 'encounters',
        'title': 'Encounters',
        'alt': 'Иконка страницы Encounters',
        'order': 100,
        'image': 'assets/page-icon/encounters/encounters.png',
    },
    {
        'key': 'synergies',
        'title': 'Synergies',
        'alt': 'Иконка страницы Synergies',
        'order': 110,
        'image': 'assets/page-icon/synergies/synergies.png',
    },
    {
        'key': 'leveling',
        'title': 'Leveling',
        'alt': 'Иконка страницы Leveling',
        'order': 120,
        'image': 'assets/page-icon/leveling/leveling.png',
    },
    {
        'key': 'faq',
        'title': 'FAQ',
        'alt': 'Иконка страницы FAQ',
        'order': 130,
        'image': 'assets/page-icon/faq/faq.png',
    },
    {
        'key': 'tracker',
        'title': 'Tracker',
        'alt': 'Иконка страницы Tracker',
        'order': 140,
        'image': 'assets/page-icon/tracker/tracker.png',
    },
    {
        'key': 'checklist',
        'title': 'Checklist',
        'alt': 'Иконка страницы Checklist',
        'order': 150,
        'image': 'assets/page-icon/checklist/checklist.png',
    },
    {
        'key': 'route',
        'title': 'Route / Plan',
        'alt': 'Иконка страницы Route / Plan',
        'order': 160,
        'image': 'assets/page-icon/route/route.png',
    },
    {
        'key': 'notes',
        'title': 'Notes',
        'alt': 'Иконка страницы Notes',
        'order': 170,
        'image': 'assets/page-icon/notes/notes.png',
    },
    {
        'key': 'setup',
        'title': 'Setup / Prep',
        'alt': 'Иконка страницы Setup / Prep',
        'order': 180,
        'image': 'assets/page-icon/setup/setup.png',
    },
    {
        'key': 'stats',
        'title': 'Stats',
        'alt': 'Иконка страницы Stats',
        'order': 190,
        'image': 'assets/page-icon/stats/stats.png',
    },
    {
        'key': 'default',
        'title': 'Default',
        'alt': 'Иконка страницы Default',
        'order': 200,
        'image': 'assets/page-icon/default/default.png',
    },
]

VALID_ICON_KEYS = {item['key'] for item in BUILTIN_ICON_DEFINITIONS}

ICON_ALIASES = {
    'overview': 'overview',
    'menu': 'overview',
    'main': 'overview',
    'home': 'overview',
    'start': 'start',
    'begin': 'start',
    'intro': 'start',
    'progression': 'progression',
    'progress': 'progression',
    'build': 'progression',
    'reference': 'reference',
    'ref': 'reference',
    'tips': 'tips',
    'tip': 'tips',
    'mistakes': 'mistakes',
    'mistake': 'mistakes',
    'errors': 'mistakes',
    'error': 'mistakes',
    'tactics': 'tactics',
    'tactic': 'tactics',
    'strategy': 'tactics',
    'strategies': 'tactics',
    'traits': 'traits',
    'trait': 'traits',
    'skills': 'traits',
    'skill': 'traits',
    'dice': 'dice',
    'die': 'dice',
    'encounters': 'encounters',
    'encounter': 'encounters',
    'battle': 'encounters',
    'synergies': 'synergies',
    'synergy': 'synergies',
    'teamwork': 'synergies',
    'leveling': 'leveling',
    'level': 'leveling',
    'faq': 'faq',
    'questions': 'faq',
    'tracker': 'tracker',
    'track': 'tracker',
    'checklist': 'checklist',
    'check': 'checklist',
    'route': 'route',
    'plan': 'route',
    'path': 'route',
    'notes': 'notes',
    'note': 'notes',
    'setup': 'setup',
    'prep': 'setup',
    'preparation': 'setup',
    'stats': 'stats',
    'stat': 'stats',
    'default': 'default',
}


def normalize_icon_token(value: str) -> str:
    return slugify(value or '').replace('-', '_').strip('_')


def resolve_icon_alias(value: str) -> str | None:
    if not value:
        return None

    normalized = normalize_icon_token(value)
    if not normalized:
        return None

    if normalized in VALID_ICON_KEYS:
        return normalized

    return ICON_ALIASES.get(normalized)


def re_split_tokens(value: str) -> list[str]:
    normalized = slugify(value or '').replace('-', ' ')
    return [part for part in normalized.split() if part]


def resolve_page_icon_key(page) -> str:
    explicit_icon = resolve_icon_alias(getattr(page, 'icon_key', ''))
    if explicit_icon:
        return explicit_icon

    for raw_value in (
        getattr(page, 'code', ''),
        getattr(page, 'slug', ''),
        getattr(page, 'title', ''),
    ):
        resolved = resolve_icon_alias(raw_value)
        if resolved:
            return resolved

        for token in re_split_tokens(raw_value):
            resolved = resolve_icon_alias(token)
            if resolved:
                return resolved

    return DEFAULT_ICON_KEY


def build_icon_static_path(page_or_key) -> str:
    if isinstance(page_or_key, str):
        icon_key = resolve_icon_alias(page_or_key) or DEFAULT_ICON_KEY
    else:
        icon_key = resolve_page_icon_key(page_or_key)

    return f'{ICON_STATIC_PREFIX}/{icon_key}.svg'


def resolve_page_icon_url(page) -> str:
    icon = getattr(page, 'icon', None)
    if icon and getattr(icon, 'image', None):
        try:
            return icon.image.url
        except ValueError:
            pass

    return static(build_icon_static_path(page))
