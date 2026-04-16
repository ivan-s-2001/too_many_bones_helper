from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Hero


def hero_detail(request, hero_slug, page_slug=None):
    hero = get_object_or_404(
        Hero.objects.select_related('portrait').filter(is_published=True),
        slug=hero_slug,
    )
    pages = hero.pages.filter(is_published=True).order_by('order', 'title')

    if page_slug:
        current_page = get_object_or_404(pages, slug=page_slug)
    else:
        current_page = pages.first()
        if current_page is None:
            raise Http404('No published pages found for this hero.')

    return render(
        request,
        'heroes/hero_detail.html',
        {
            'hero': hero,
            'current_page': current_page,
            'pages': pages,
        },
    )
