from django.shortcuts import render

from heroes.models import Hero


def home(request):
    heroes = (
        Hero.objects.filter(is_published=True)
        .select_related('portrait')
        .order_by('order', 'name')
    )

    return render(
        request,
        'web/home.html',
        {
            'heroes': heroes,
        },
    )
