from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('organization_structure_api.api.urls', namespace='api')),
    
    #Other pages(Landing,etc..)
]
