from django.urls import path

from departments.api.views import (
    DepartmentCreateAPIView,
    DepartmentDetailAPIView,
)

app_name = "departments_api"

urlpatterns = [
    path("departments/", DepartmentCreateAPIView.as_view(), name="department-create"),
    path("departments/<int:pk>/", DepartmentDetailAPIView.as_view(), name="department-detail"),
]