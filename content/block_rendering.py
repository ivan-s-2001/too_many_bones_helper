from __future__ import annotations


TEXT_BLOCK_TEMPLATE = 'content/blocks/text.html'
UNSUPPORTED_BLOCK_TEMPLATE = 'content/blocks/unsupported.html'


def prepare_sections_for_render(sections):
    prepared_sections = []

    for section in sections:
        published_blocks = getattr(section, 'published_blocks', [])
        section.render_blocks = [prepare_block_for_render(block) for block in published_blocks]
        prepared_sections.append(section)

    return prepared_sections


def prepare_block_for_render(block):
    block.render_template = get_block_template(block)
    block.text_paragraphs = get_text_paragraphs(block)
    return block


def get_block_template(block) -> str:
    if block.type == 'text':
        return TEXT_BLOCK_TEMPLATE

    return UNSUPPORTED_BLOCK_TEMPLATE


def get_text_paragraphs(block):
    if block.type != 'text':
        return []

    data = block.data if isinstance(block.data, dict) else {}
    raw_text = data.get('text', '')

    if not raw_text:
        return []

    normalized_text = str(raw_text).replace('\r\n', '\n').strip()

    if not normalized_text:
        return []

    return [paragraph.strip() for paragraph in normalized_text.split('\n\n') if paragraph.strip()]
