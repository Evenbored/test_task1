import pytest
from rest_framework import status
from rest_framework.test import APIClient

from departments.models import Department
from employees.models import Employee

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_create_employee_in_department(api_client):
    department = Department.objects.create(name="Backend")

    response = api_client.post(
        f"/api/v1/departments/{department.id}/employees/",
        {
            "full_name": "Ivan Petrov",
            "position": "Developer",
            "hired_at": "2024-01-15",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["full_name"] == "Ivan Petrov"
    assert response.data["position"] == "Developer"
    assert response.data["hired_at"] == "2024-01-15"
    assert Employee.objects.filter(
        department=department,
        full_name="Ivan Petrov",
        position="Developer",
    ).exists()

@pytest.mark.django_db
def test_create_employee_in_missing_department_returns_404(api_client):
    response = api_client.post(
        "/api/v1/departments/999/employees/",
        {
            "full_name": "Ivan Petrov",
            "position": "Developer",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND