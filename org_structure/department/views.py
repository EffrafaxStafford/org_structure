from django.shortcuts import get_object_or_404
from rest_framework import generics

from .models import Department, Employee
from .serializers import DepartmentSerializer, EmployeeSerializer


class DepartmentCreateAPIView(generics.CreateAPIView):
    """Создать подразделение."""

    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()


class EmployeeCreateAPIView(generics.CreateAPIView):
    """Создать сотрудника."""

    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()

    def perform_create(self, serializer):
        department = get_object_or_404(
            Department,
            pk=self.kwargs['id'],
        )
        serializer.save(department=department)

