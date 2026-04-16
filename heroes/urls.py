from django.urls import path

from .views import hero_detail

app_name = 'heroes'

urlpatterns = [
    path('<slug:hero_slug>/', hero_detail, name='detail'),
    path('<slug:hero_slug>/<slug:page_slug>/', hero_detail, name='page_detail'),
]
