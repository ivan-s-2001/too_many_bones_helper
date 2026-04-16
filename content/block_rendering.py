from __future__ import annotations

from typing import Any


TEXT_BLOCK_TEMPLATE = 'content/blocks/text.html'
LIST_BLOCK_TEMPLATE = 'content/blocks/list.html'
FACT_BLOCK_TEMPLATE = 'content/blocks/fact.html'
ACCENT_BLOCK_TEMPLATE = 'content/blocks/accent.html'
CARDS_BLOCK_TEMPLATE = 'content/blocks/cards.html'
CHECKLIST_BLOCK_TEMPLATE = 'content/blocks/checklist.html'
UNSUPPORTED_BLOCK_TEMPLATE = 'content/blocks/unsupported.html'


BLOCK_TEMPLATE_MAP = {
    'text': TEXT_BLOCK_TEMPLATE,
    'list': LIST_BLOCK_TEMPLATE,
    'fact': FACT_BLOCK_TEMPLATE,
    'accent': ACCENT_BLOCK_TEMPLATE,
    'cards': CARDS_BLOCK_TEMPLATE,
    'checklist': CHECKLIST_BLOCK_TEMPLATE,
}



def prepare_sections_for_render(sections):
    prepared_sections = []

    for section in sections:
        published_blocks = getattr(section, 'published_blocks', [])
        section.render_blocks = [prepare_block_for_render(block) for block in published_blocks]
        prepared_sections.append(section)

    return prepared_sections



def prepare_block_for_render(block):
    block.render_template = get_block_template(block)

    data = block.data if isinstance(block.data, dict) else {}
    block.text_paragraphs = get_text_paragraphs(data)
    block.list_intro = str(data.get('intro') or '').strip() if block.type == 'list' else ''
    block.list_items = get_list_items(data) if block.type == 'list' else []
    block.fact_value, block.fact_label, block.fact_description = get_fact_data(block.type, data)
    block.accent_badge, block.accent_text, block.accent_note = get_accent_data(block.type, data)
    block.cards_intro = str(data.get('intro') or '').strip() if block.type == 'cards' else ''
    block.cards_items = get_cards_items(block.type, data)
    block.checklist_intro = str(data.get('intro') or '').strip() if block.type == 'checklist' else ''
    block.checklist_items = get_checklist_items(block.type, data)
    block.checklist_checked_count = sum(1 for item in block.checklist_items if item['checked'])
    block.checklist_total_count = len(block.checklist_items)
    return block



def get_block_template(block) -> str:
    return BLOCK_TEMPLATE_MAP.get(block.type, UNSUPPORTED_BLOCK_TEMPLATE)



def get_text_paragraphs(data: dict[str, Any]) -> list[str]:
    raw_text = data.get('text', '')
    normalized_text = str(raw_text).replace('\r\n', '\n').strip()

    if not normalized_text:
        return []

    return [paragraph.strip() for paragraph in normalized_text.split('\n\n') if paragraph.strip()]



def get_list_items(data: dict[str, Any]) -> list[str]:
    raw_items = data.get('items', [])
    if not isinstance(raw_items, list):
        return []
    return [str(item).strip() for item in raw_items if str(item).strip()]



def get_fact_data(block_type: str, data: dict[str, Any]) -> tuple[str, str, str]:
    if block_type != 'fact':
        return '', '', ''

    return (
        str(data.get('value') or '').strip(),
        str(data.get('label') or '').strip(),
        str(data.get('description') or '').strip(),
    )



def get_accent_data(block_type: str, data: dict[str, Any]) -> tuple[str, str, str]:
    if block_type != 'accent':
        return '', '', ''

    return (
        str(data.get('badge') or '').strip(),
        str(data.get('text') or '').strip(),
        str(data.get('note') or '').strip(),
    )



def get_cards_items(block_type: str, data: dict[str, Any]) -> list[dict[str, str]]:
    if block_type != 'cards':
        return []

    raw_items = data.get('items', [])
    if not isinstance(raw_items, list):
        return []

    cards: list[dict[str, str]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        title = str(item.get('title') or '').strip()
        text = str(item.get('text') or '').strip()
        if not title and not text:
            continue
        cards.append(
            {
                'title': title,
                'text': text,
            }
        )
    return cards



def get_checklist_items(block_type: str, data: dict[str, Any]) -> list[dict[str, Any]]:
    if block_type != 'checklist':
        return []

    raw_items = data.get('items', [])
    if not isinstance(raw_items, list):
        return []

    checklist_items: list[dict[str, Any]] = []
    for item in raw_items:
        if isinstance(item, dict):
            text = str(item.get('text') or '').strip()
            checked = bool(item.get('checked'))
        else:
            text = str(item).strip()
            checked = False

        if not text:
            continue

        checklist_items.append(
            {
                'text': text,
                'checked': checked,
            }
        )
    return checklist_items
