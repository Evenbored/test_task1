from django.urls import path
from .views import DepartmentEmployeeCreateAPIView

app_name = "employees"

urlpatterns = [
    path("departments/<int:pk>/employees/", DepartmentEmployeeCreateAPIView.as_view(), name="department-employee-create"),
]