from django.urls import path

from .views import hero_detail

app_name = 'heroes'

urlpatterns = [
    path('<slug:slug>/', hero_detail, name='detail'),
]
