from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('heroes/', include('heroes.urls')),
    path('', include('web.urls')),
]
