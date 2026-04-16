from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Too Many Bones — редактор контента'
admin.site.site_title = 'Too Many Bones Admin'
admin.site.index_title = 'Герои, страницы, секции и блоки'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('heroes/', include('heroes.urls')),
    path('', include('web.urls')),
]
