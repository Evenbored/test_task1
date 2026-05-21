

from django.urls import include, path


app_name = "api"

urlpatterns = [
    path("", include("departments.api.urls")),
    path("", include("employees.api.urls")),
]