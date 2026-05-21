from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache

from departments.api.serializers import (
    DepartmentCreateSerializer,
    DepartmentDetailSerializer,
    DepartmentShortSerializer,
    DepartmentUpdateSerializer,
)
from departments.models import Department

class DepartmentCreateAPIView(APIView):
    def post(self, request):
        serializer = DepartmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department = serializer.save()
        cache.clear()
        response_serializer = DepartmentShortSerializer(department)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class DepartmentDetailAPIView(APIView):
    def get(self, request, pk):
        department = get_object_or_404(Department, pk=pk)

        depth = request.query_params.get("depth", 1)
        include_employees = request.query_params.get("include_employees", "true")

        try:
            depth = int(depth)
        except (TypeError, ValueError):
            return Response(
                {"depth": "Depth must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if depth < 1 or depth > 5:
            return Response(
                {"depth": "Depth must be between 1 and 5."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        include_employees = str(include_employees).lower() not in ("false", "0", "no")

        cache_key = f"department:{pk}:depth:{depth}:employees:{include_employees}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)
        serializer = DepartmentDetailSerializer(
            department,
            context={
                "depth": depth,
                "include_employees": include_employees,
            },
        )
        cache.set(cache_key, serializer.data, timeout=300)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        department = get_object_or_404(Department, pk=pk)

        serializer = DepartmentUpdateSerializer(
            department,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        new_parent = serializer.validated_data.get("parent", department.parent)

        if new_parent is not None:
            if new_parent.pk == department.pk:
                return Response(
                    {"parent_id": "Department cannot be parent of itself."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if self._is_descendant(parent=department, child=new_parent):
                return Response(
                    {"parent_id": "Cannot move department inside its own subtree."},
                    status=status.HTTP_409_CONFLICT,
                )

        updated_department = serializer.save()
        cache.clear()

        response_serializer = DepartmentShortSerializer(updated_department)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk):
        department = get_object_or_404(Department, pk=pk)

        mode = request.query_params.get("mode")

        if mode not in ("cascade", "reassign"):
            return Response(
                {"mode": "Mode must be either 'cascade' or 'reassign'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if mode == "cascade":
            department.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        reassign_to_department_id = request.query_params.get("reassign_to_department_id")

        if not reassign_to_department_id:
            return Response(
                {
                    "reassign_to_department_id": (
                        "This query parameter is required when mode='reassign'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reassign_to_department_id = int(reassign_to_department_id)
        except (TypeError, ValueError):
            return Response(
                {"reassign_to_department_id": "Must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reassign_to_department_id == department.pk:
            return Response(
                {
                    "reassign_to_department_id": (
                        "Cannot reassign employees to department being deleted."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reassign_to_department = get_object_or_404(
            Department,
            pk=reassign_to_department_id,
        )

        if self._is_descendant(parent=department, child=reassign_to_department):
            return Response(
            {
                "reassign_to_department_id": (
                    "Cannot reassign employees to department inside deleted subtree."
                )
            },
            status=status.HTTP_409_CONFLICT,
            )
        
        department.employees.update(department=reassign_to_department)
        
        department.delete()
        cache.clear()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def _is_descendant(self, parent: Department, child: Department) -> bool:
        current = child.parent

        while current is not None:
            if current.pk == parent.pk:
                return True

            current = current.parent

        return False