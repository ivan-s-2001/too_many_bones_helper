from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from content.block_rendering import prepare_sections_for_render
from content.models import Block

from .models import Hero


def hero_detail(request, hero_slug, page_slug=None):
    hero = get_object_or_404(
        Hero.objects.select_related('portrait').filter(is_published=True),
        slug=hero_slug,
    )
    pages = (
        hero.pages
        .select_related('icon')
        .filter(is_published=True)
        .order_by('order', 'title')
    )

    if page_slug:
        current_page = get_object_or_404(pages, slug=page_slug)
    else:
        current_page = pages.first()
        if current_page is None:
            raise Http404('No published pages found for this hero.')

    sections = list(
        current_page.sections
        .filter(is_published=True)
        .prefetch_related(
            Prefetch(
                'blocks',
                queryset=Block.objects.filter(is_published=True).order_by('order', 'id'),
                to_attr='published_blocks',
            )
        )
        .order_by('order', 'title')
    )
    prepare_sections_for_render(sections)

    return render(
        request,
        'heroes/hero_detail.html',
        {
            'hero': hero,
            'current_page': current_page,
            'pages': pages,
            'sections': sections,
        },
    )
