from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from django import forms


EDITOR_FIELD_ATTR = 'data-block-editor-type'
FALLBACK_FIELD_ATTR = 'data-block-editor-fallback'


class BlockEditorRegistry:
    def __init__(self) -> None:
        self._editors: dict[str, type[BaseBlockEditor]] = {}

    def register(self, editor_class: type['BaseBlockEditor']) -> type['BaseBlockEditor']:
        self._editors[editor_class.block_type] = editor_class
        return editor_class

    def get(self, block_type: str | None) -> type['BaseBlockEditor'] | None:
        if not block_type:
            return None
        return self._editors.get(block_type.strip().lower())

    def all(self) -> list[type['BaseBlockEditor']]:
        return list(self._editors.values())

    def supported_types(self) -> tuple[str, ...]:
        return tuple(self._editors.keys())

    def all_field_names(self) -> list[str]:
        field_names: list[str] = []
        for editor in self.all():
            field_names.extend(editor.field_order)
        return field_names


block_editor_registry = BlockEditorRegistry()


@dataclass(frozen=True)
class EditorPresentation:
    name: str
    description: str


class BaseBlockEditor:
    block_type = ''
    presentation = EditorPresentation(name='', description='')
    field_definitions: dict[str, forms.Field] = {}
    field_order: tuple[str, ...] = ()

    @classmethod
    def build_form_fields(cls) -> dict[str, forms.Field]:
        fields: dict[str, forms.Field] = {}
        for field_name in cls.field_order:
            field = deepcopy(cls.field_definitions[field_name])
            existing_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_class} vLargeTextField'.strip()
            field.widget.attrs[EDITOR_FIELD_ATTR] = cls.block_type
            field.widget.attrs['data-block-editor-field'] = field_name
            fields[field_name] = field
        return fields

    @classmethod
    def get_initial_from_data(cls, data: Any) -> dict[str, Any]:
        return {}

    @classmethod
    def build_data_from_cleaned_data(cls, cleaned_data: dict[str, Any]) -> dict[str, Any]:
        return {}

    @classmethod
    def summary(cls) -> str:
        return cls.presentation.description



def compact_dict(data: dict[str, Any]) -> dict[str, Any]:
    compacted: dict[str, Any] = {}
    for key, value in data.items():
        if value in (None, '', [], {}):
            continue
        compacted[key] = value
    return compacted



def normalize_dict(data: Any) -> dict[str, Any]:
    if isinstance(data, dict):
        return data
    return {}



def split_lines(value: Any) -> list[str]:
    normalized_text = str(value or '').replace('\r\n', '\n')
    return [line.strip() for line in normalized_text.split('\n') if line.strip()]



def split_paragraphs(value: Any) -> list[str]:
    normalized_text = str(value or '').replace('\r\n', '\n').strip()
    if not normalized_text:
        return []
    return [chunk.strip() for chunk in normalized_text.split('\n\n') if chunk.strip()]



def serialize_cards(items: list[dict[str, str]]) -> str:
    chunks: list[str] = []
    for item in items:
        title = str(item.get('title') or '').strip()
        text = str(item.get('text') or '').strip()
        if not title and not text:
            continue
        parts = [part for part in (title, text) if part]
        chunks.append('\n'.join(parts))
    return '\n\n'.join(chunks)



def parse_cards(raw_value: Any) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for chunk in split_paragraphs(raw_value):
        lines = [line.strip() for line in chunk.split('\n') if line.strip()]
        if not lines:
            continue
        title = lines[0]
        text = '\n'.join(lines[1:]).strip()
        card = compact_dict(
            {
                'title': title,
                'text': text,
            }
        )
        if card:
            cards.append(card)
    return cards



def serialize_checklist(items: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for item in items:
        text = str(item.get('text') or '').strip()
        if not text:
            continue
        checked = bool(item.get('checked'))
        prefix = '[x]' if checked else '[ ]'
        lines.append(f'{prefix} {text}')
    return '\n'.join(lines)



def parse_checklist(raw_value: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in split_lines(raw_value):
        checked = False
        text = line
        lowered = line.lower()

        if lowered.startswith('[x]'):
            checked = True
            text = line[3:].strip()
        elif lowered.startswith('[ ]'):
            text = line[3:].strip()
        elif line.startswith('+ '):
            checked = True
            text = line[2:].strip()
        elif line.startswith('- '):
            text = line[2:].strip()
        elif line.startswith('✓ '):
            checked = True
            text = line[2:].strip()

        if not text:
            continue

        items.append(
            {
                'text': text,
                'checked': checked,
            }
        )
    return items


@block_editor_registry.register
class TextBlockEditor(BaseBlockEditor):
    block_type = 'text'
    presentation = EditorPresentation(
        name='Текст',
        description='Обычный текстовый блок. Можно вставить несколько абзацев, JSON соберётся автоматически.',
    )
    field_definitions = {
        'editor_text_body': forms.CharField(
            label='Текст блока',
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': 10,
                    'placeholder': 'Введите основной текст. Для нового абзаца оставьте пустую строку.',
                }
            ),
            help_text='Поддерживаются несколько абзацев. Каждый абзац отделяйте пустой строкой.',
        ),
    }
    field_order = ('editor_text_body',)

    @classmethod
    def get_initial_from_data(cls, data: Any) -> dict[str, Any]:
        payload = normalize_dict(data)
        return {
            'editor_text_body': payload.get('text', ''),
        }

    @classmethod
    def build_data_from_cleaned_data(cls, cleaned_data: dict[str, Any]) -> dict[str, Any]:
        return compact_dict(
            {
                'text': str(cleaned_data.get('editor_text_body') or '').strip(),
            }
        )


@block_editor_registry.register
class ListBlockEditor(BaseBlockEditor):
    block_type = 'list'
    presentation = EditorPresentation(
        name='Список',
        description='Вводите вступление и пункты списка. Каждый пункт — с новой строки.',
    )
    field_definitions = {
        'editor_list_intro': forms.CharField(
            label='Вступление к списку',
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Короткое вводное пояснение перед списком.',
                }
            ),
            help_text='Необязательный короткий текст перед пунктами.',
        ),
        'editor_list_items': forms.CharField(
            label='Пункты списка',
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': 8,
                    'placeholder': 'Каждый пункт начинайте с новой строки.',
                }
            ),
            help_text='Один пункт — одна строка.',
        ),
    }
    field_order = ('editor_list_intro', 'editor_list_items')

    @classmethod
    def get_initial_from_data(cls, data: Any) -> dict[str, Any]:
        payload = normalize_dict(data)
        items = payload.get('items', [])
        return {
            'editor_list_intro': payload.get('intro', ''),
            'editor_list_items': '\n'.join(str(item).strip() for item in items if str(item).strip()),
        }

    @classmethod
    def build_data_from_cleaned_data(cls, cleaned_data: dict[str, Any]) -> dict[str, Any]:
        return compact_dict(
            {
                'intro': str(cleaned_data.get('editor_list_intro') or '').strip(),
                'items': split_lines(cleaned_data.get('editor_list_items')),
            }
        )


@block_editor_registry.register
class FactBlockEditor(BaseBlockEditor):
    block_type = 'fact'
    presentation = EditorPresentation(
        name='Факт',
        description='Крупный факт или показатель: значение, подпись и краткое пояснение.',
    )
    field_definitions = {
        'editor_fact_value': forms.CharField(
            label='Главное значение',
            required=False,
            widget=forms.TextInput(
                attrs={
                    'placeholder': 'Например: 3, 12+, 90%',
                }
            ),
            help_text='Крупная цифра, короткое значение или важная пометка.',
        ),
        'editor_fact_label': forms.CharField(
            label='Подпись к значению',
            required=False,
            widget=forms.TextInput(
                attrs={
                    'placeholder': 'Например: Кубики защиты',
                }
            ),
            help_text='Короткая подпись под главным значением.',
        ),
        'editor_fact_description': forms.CharField(
            label='Пояснение',
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Дополнительный контекст или пояснение.',
                }
            ),
            help_text='Необязательный текст под фактом.',
        ),
    }
    field_order = ('editor_fact_value', 'editor_fact_label', 'editor_fact_description')

    @classmethod
    def get_initial_from_data(cls, data: Any) -> dict[str, Any]:
        payload = normalize_dict(data)
        return {
            'editor_fact_value': payload.get('value', ''),
            'editor_fact_label': payload.get('label', ''),
            'editor_fact_description': payload.get('description', ''),
        }

    @classmethod
    def build_data_from_cleaned_data(cls, cleaned_data: dict[str, Any]) -> dict[str, Any]:
        return compact_dict(
            {
                'value': str(cleaned_data.get('editor_fact_value') or '').strip(),
                'label': str(cleaned_data.get('editor_fact_label') or '').strip(),
                'description': str(cleaned_data.get('editor_fact_description') or '').strip(),
            }
        )


@block_editor_registry.register
class AccentBlockEditor(BaseBlockEditor):
    block_type = 'accent'
    presentation = EditorPresentation(
        name='Акцент',
        description='Выделенный акцентный блок для важной мысли, заметки или совета.',
    )
    field_definitions = {
        'editor_accent_badge': forms.CharField(
            label='Метка',
            required=False,
            widget=forms.TextInput(
                attrs={
                    'placeholder': 'Например: Важно',
                }
            ),
            help_text='Короткая метка в верхней части блока.',
        ),
        'editor_accent_text': forms.CharField(
            label='Основной акцентный текст',
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Главная мысль, которую нужно выделить.',
                }
            ),
            help_text='Главный текст акцентного блока.',
        ),
        'editor_accent_note': forms.CharField(
            label='Дополнительная заметка',
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Короткое пояснение или комментарий.',
                }
            ),
            help_text='Необязательное пояснение под главным текстом.',
        ),
    }
    field_order = ('editor_accent_badge', 'editor_accent_text', 'editor_accent_note')

    @classmethod
    def get_initial_from_data(cls, data: Any) -> dict[str, Any]:
        payload = normalize_dict(data)
        return {
            'editor_accent_badge': payload.get('badge', ''),
            'editor_accent_text': payload.get('text', ''),
            'editor_accent_note': payload.get('note', ''),
        }

    @classmethod
    def build_data_from_cleaned_data(cls, cleaned_data: dict[str, Any]) -> dict[str, Any]:
        return compact_dict(
            {
                'badge': str(cleaned_data.get('editor_accent_badge') or '').strip(),
                'text': str(cleaned_data.get('editor_accent_text') or '').strip(),
                'note': str(cleaned_data.get('editor_accent_note') or '').strip(),
            }
        )


@block_editor_registry.register
class CardsBlockEditor(BaseBlockEditor):
    block_type = 'cards'
    presentation = EditorPresentation(
        name='Карточки',
        description='Набор карточек. Каждая карточка отделяется пустой строкой: первая строка — заголовок, ниже — текст.',
    )
    field_definitions = {
        'editor_cards_intro': forms.CharField(
            label='Вступление к карточкам',
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Короткий вводный текст перед набором карточек.',
                }
            ),
            help_text='Необязательный текст над сеткой карточек.',
        ),
        'editor_cards_items': forms.CharField(
            label='Карточки',
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': 12,
                    'placeholder': 'Карточка 1\nОписание карточки\n\nКарточка 2\nЕщё одно описание',
                }
            ),
            help_text='Каждая карточка отделяется пустой строкой. Первая строка — заголовок. Остальные строки — описание.',
        ),
    }
    field_order = ('editor_cards_intro', 'editor_cards_items')

    @classmethod
    def get_initial_from_data(cls, data: Any) -> dict[str, Any]:
        payload = normalize_dict(data)
        items = payload.get('items', []) if isinstance(payload.get('items'), list) else []
        return {
            'editor_cards_intro': payload.get('intro', ''),
            'editor_cards_items': serialize_cards(items),
        }

    @classmethod
    def build_data_from_cleaned_data(cls, cleaned_data: dict[str, Any]) -> dict[str, Any]:
        return compact_dict(
            {
                'intro': str(cleaned_data.get('editor_cards_intro') or '').strip(),
                'items': parse_cards(cleaned_data.get('editor_cards_items')),
            }
        )


@block_editor_registry.register
class ChecklistBlockEditor(BaseBlockEditor):
    block_type = 'checklist'
    presentation = EditorPresentation(
        name='Чеклист',
        description='Список пунктов с состоянием. Используйте [x] для выполненного и [ ] для обычного пункта.',
    )
    field_definitions = {
        'editor_checklist_intro': forms.CharField(
            label='Вступление к чеклисту',
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Короткое пояснение перед чеклистом.',
                }
            ),
            help_text='Необязательное пояснение перед списком.',
        ),
        'editor_checklist_items': forms.CharField(
            label='Пункты чеклиста',
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': 10,
                    'placeholder': '[x] Выполненный пункт\n[ ] Обычный пункт',
                }
            ),
            help_text='Каждый пункт — с новой строки. Для выполненных используйте [x], для обычных — [ ].',
        ),
    }
    field_order = ('editor_checklist_intro', 'editor_checklist_items')

    @classmethod
    def get_initial_from_data(cls, data: Any) -> dict[str, Any]:
        payload = normalize_dict(data)
        items = payload.get('items', []) if isinstance(payload.get('items'), list) else []
        return {
            'editor_checklist_intro': payload.get('intro', ''),
            'editor_checklist_items': serialize_checklist(items),
        }

    @classmethod
    def build_data_from_cleaned_data(cls, cleaned_data: dict[str, Any]) -> dict[str, Any]:
        return compact_dict(
            {
                'intro': str(cleaned_data.get('editor_checklist_intro') or '').strip(),
                'items': parse_checklist(cleaned_data.get('editor_checklist_items')),
            }
        )


SUPPORTED_BLOCK_TYPE_PRESENTATIONS = {
    editor.block_type: editor.presentation for editor in block_editor_registry.all()
}
