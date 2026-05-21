from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from departments.models import Department
from employees.api.serializers import EmployeeCreateSerializer, EmployeeShortSerializer

class DepartmentEmployeeCreateAPIView(APIView):
    def post(self, request, pk):
        department = get_object_or_404(Department, pk=pk)

        serializer = EmployeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee = serializer.save(department=department)
        cache.clear()
        response_serializer = EmployeeShortSerializer(employee)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)