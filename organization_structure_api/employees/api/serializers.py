from rest_framework import serializers

from employees.models import Employee

class EmployeeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("id", "full_name", "position", "hired_at", "created_at")
        read_only_fields = fields

class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("full_name", "position", "hired_at")
    
    def validate_full_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("full_name cannot be empty.")
        return value

    def validate_position(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("position cannot be empty.")
        return value