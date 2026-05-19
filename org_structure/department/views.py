from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Department, Employee
from .serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    DepartmentTreeSerializer,
    DepartmentUpdateSerializer,
)
from config.constants import MIN_DEPTH, MAX_DEPTH


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


class DepartmentDetailAPIView(APIView):
    """Получить информацию о подразделении."""

    def get(self, request, id):
        department = get_object_or_404(
            Department.objects.prefetch_related(
                'employees',
                'children',
            ),
            pk=id,
        )

        depth = self._get_depth_from_query(request)

        include_employees = (
            request.query_params.get(
                'include_employees',
                'true',
            ).lower() == 'true'
        )

        serializer = DepartmentTreeSerializer(
            department,
            context={
                'depth': depth,
                'include_employees': include_employees,
            }
        )

        return Response(serializer.data)

    def _get_depth_from_query(self, request):
        """Получить параметр depth из запроса и проверить его валидность."""

        raw_depth = request.query_params.get('depth')

        if raw_depth is None:
            return MIN_DEPTH

        try:
            depth = int(raw_depth)
        except (TypeError, ValueError):
            raise ValidationError({
                'depth': f'Параметр depth должен быть целым числом от {MIN_DEPTH} до {MAX_DEPTH}.'
            })

        if depth < MIN_DEPTH or depth > MAX_DEPTH:
            raise ValidationError({
                'depth': f'Параметр depth должен быть целым числом от {MIN_DEPTH} до {MAX_DEPTH}.'
            })

        return depth

    def patch(self, request, id):
        department = get_object_or_404(Department, pk=id)

        serializer = DepartmentUpdateSerializer(
            department,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, id):
        department = get_object_or_404(
            Department,
            pk=id,
        )

        mode = request.query_params.get('mode')
        if mode is None:
            raise ValidationError({
                'mode': 'Этот параметр запроса обязателен и должен быть равен "cascade" или "reassign".'
            })

        if mode == 'cascade':
            department.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if mode == 'reassign':
            reassign_to_department_id = request.query_params.get(
                'reassign_to_department_id',
            )

            if not reassign_to_department_id:
                raise ValidationError({
                    'reassign_to_department_id': 'Этот параметр запроса обязателен при mode=reassign.'
                })

            reassign_to_department = get_object_or_404(
                Department,
                pk=reassign_to_department_id,
            )

            if reassign_to_department.id == department.id:
                raise ValidationError({
                    'reassign_to_department_id': 'Нельзя переназначить сотрудников в удаленное подразделение.'
                })

            department.children.update(
                parent=reassign_to_department,
            )

            department.employees.update(
                department=reassign_to_department,
            )

            department.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
