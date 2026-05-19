import pytest
from rest_framework.test import APIClient

from department.models import Department, Employee


@pytest.fixture
def api_client():
    """Клиент для тестирования API."""
    return APIClient()


@pytest.fixture
def root_department(db):
    """Корневое подразделение."""
    return Department.objects.create(name='Root')


@pytest.fixture
def source_department(db, root_department):
    """Подразделение, из которого будет перемещаться сотрудник."""
    return Department.objects.create(
        name='Source',
        parent=root_department,
    )


@pytest.fixture
def child_department(db, source_department):
    """Дочернее подразделение."""
    return Department.objects.create(
        name='Child',
        parent=source_department,
    )


@pytest.fixture
def target_department(db, root_department):
    """Подразделение, в которое будет перемещаться сотрудник."""
    return Department.objects.create(
        name='Target',
        parent=root_department,
    )


@pytest.fixture
def source_employee(db, source_department):
    """Сотрудник, который будет перемещаться из source_department в target_department."""
    return Employee.objects.create(
        department=source_department,
        full_name='Moved Employee',
        position='Engineer',
    )


@pytest.fixture
def child_employee(db, child_department):
    """Сотрудник, который будет перемещаться из child_department в target_department."""
    return Employee.objects.create(
        department=child_department,
        full_name='Child Employee',
        position='Engineer',
    )
