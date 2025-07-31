# fresh_app/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from portal.views import admin_dashboard

# This line tells the admin site to use our custom view as its homepage.
admin.site.index = admin_dashboard

urlpatterns = [
    # The standard, single admin path.
    # It will now automatically show our custom dashboard.
    path('admin/', admin.site.urls), 
    
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('portal.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
