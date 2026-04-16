from django.shortcuts import get_object_or_404, render

from .models import Hero


def hero_detail(request, slug):
    hero = get_object_or_404(
        Hero.objects.filter(is_published=True),
        slug=slug,
    )

    return render(
        request,
        'heroes/hero_detail.html',
        {
            'hero': hero,
        },
    )
