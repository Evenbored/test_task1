import pytest
from rest_framework import status
from rest_framework.test import APIClient

from departments.models import Department
from employees.models import Employee

@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_create_root_department(api_client):
    response = api_client.post(
        "/api/v1/departments/",
        {"name": "Backend"},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Backend"
    assert response.data["parent_id"] is None
    assert Department.objects.filter(name="Backend", parent=None).exists()

@pytest.mark.django_db
def test_create_duplicate_department_in_same_parent_fails(api_client):
    parent = Department.objects.create(name="IT")
    Department.objects.create(name="Backend", parent=parent)

    response = api_client.post(
        "/api/v1/departments/",
        {"name": "Backend", "parent_id": parent.id},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.data

@pytest.mark.django_db
def test_delete_department_cascade(api_client):
    root = Department.objects.create(name="Root")
    child = Department.objects.create(name="Child", parent=root)

    response = api_client.delete(
        f"/api/v1/departments/{root.id}/?mode=cascade"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Department.objects.filter(id=root.id).exists()
    assert not Department.objects.filter(id=child.id).exists()