from django.utils.text import slugify


ICON_CHOICES = [
    ('overview', 'Overview / Main'),
    ('start', 'Start'),
    ('progression', 'Progression / Build'),
    ('reference', 'Reference'),
    ('tips', 'Tips'),
    ('mistakes', 'Mistakes'),
    ('tactics', 'Tactics / Strategy'),
    ('traits', 'Traits / Skills'),
    ('dice', 'Dice'),
    ('encounters', 'Encounters'),
    ('synergies', 'Synergies'),
    ('leveling', 'Leveling'),
    ('faq', 'FAQ'),
    ('tracker', 'Tracker'),
    ('checklist', 'Checklist'),
    ('route', 'Route / Plan'),
    ('notes', 'Notes'),
    ('setup', 'Setup / Prep'),
    ('stats', 'Stats'),
    ('default', 'Default'),
]

DEFAULT_ICON_KEY = 'default'
VALID_ICON_KEYS = {key for key, _ in ICON_CHOICES}
ICON_STATIC_PREFIX = 'heroes/page-icons'

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


def build_icon_static_path(page) -> str:
    return f'{ICON_STATIC_PREFIX}/{resolve_page_icon_key(page)}.svg'


def re_split_tokens(value: str) -> list[str]:
    normalized = slugify(value or '').replace('-', ' ')
    return [part for part in normalized.split() if part]
