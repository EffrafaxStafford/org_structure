from rest_framework import serializers

from .models import Department, Employee


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'parent', 'created_at')
        read_only_fields = ('id', 'created_at')


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'department', 'full_name',
                  'position', 'hired_at', 'created_at')
        read_only_fields = ('id', 'department', 'created_at')
