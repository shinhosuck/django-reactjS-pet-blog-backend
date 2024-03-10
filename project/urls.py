
from django.contrib import admin
from django.urls import path, include
import debug_toolbar

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('posts.urls', namespace='posts')),
    path('api/auth/', include('users.urls', namespace='users')),
    path('api-auth/', include('rest_framework.urls')),
    path("debug/", include(debug_toolbar.urls)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)