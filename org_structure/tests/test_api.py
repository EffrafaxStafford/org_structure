import pytest
from rest_framework import status

from department.models import Department, Employee


@pytest.mark.django_db
def test_create_department_returns_created_department(api_client):
    response = api_client.post(
        '/departments/',
        {
            'name': 'Backend',
            'parent': None,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'Backend'
    assert response.data['parent'] is None
    assert Department.objects.filter(
        name='Backend',
        parent=None,
    ).exists()


@pytest.mark.django_db
def test_create_employee_in_missing_department_returns_404(api_client):
    response = api_client.post(
        '/departments/999/employees/',
        {
            'full_name': 'Ivan Petrov',
            'position': 'Developer',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_department_returns_details_employees_and_subtree(api_client):
    root = Department.objects.create(name='Head Office')
    child = Department.objects.create(
        name='Backend',
        parent=root,
    )
    grandchild = Department.objects.create(
        name='Platform',
        parent=child,
    )
    root_employee = Employee.objects.create(
        department=root,
        full_name='Boris Admin',
        position='Head',
    )
    child_employee = Employee.objects.create(
        department=child,
        full_name='Anna Developer',
        position='Engineer',
    )
    Employee.objects.create(
        department=grandchild,
        full_name='Petr Infra',
        position='SRE',
    )

    response = api_client.get(f'/departments/{root.id}/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['department']['id'] == root.id
    assert response.data['employees'][0]['id'] == root_employee.id
    assert len(response.data['children']) == 1
    assert response.data['children'][0]['department']['id'] == child.id
    assert response.data['children'][0]['employees'][0]['id'] == child_employee.id
    assert response.data['children'][0]['children'] == []


@pytest.mark.django_db
def test_get_department_respects_depth_and_include_employees(
    api_client,
    root_department,
):
    child = Department.objects.create(
        name='Child',
        parent=root_department,
    )
    grandchild = Department.objects.create(
        name='Grandchild',
        parent=child,
    )
    Employee.objects.create(
        department=root_department,
        full_name='Root Employee',
        position='Lead',
    )
    Employee.objects.create(
        department=child,
        full_name='Child Employee',
        position='Engineer',
    )
    Employee.objects.create(
        department=grandchild,
        full_name='Grandchild Employee',
        position='Engineer',
    )

    response = api_client.get(
        f'/departments/{root_department.id}/?depth=2&include_employees=false'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['employees'] == []
    assert response.data['children'][0]['employees'] == []
    assert response.data['children'][0]['children'][0]['department']['id'] == grandchild.id
    assert response.data['children'][0]['children'][0]['employees'] == []


@pytest.mark.django_db
def test_get_department_with_invalid_depth_returns_400(
    api_client,
    root_department,
):
    response = api_client.get(
        f'/departments/{root_department.id}/?depth=abc'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'depth' in response.data


@pytest.mark.django_db
def test_patch_department_rejects_cycle(
    api_client,
    root_department,
):
    child = Department.objects.create(
        name='Child',
        parent=root_department,
    )

    response = api_client.patch(
        f'/departments/{root_department.id}/',
        {
            'parent': child.id,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'parent' in response.data


@pytest.mark.django_db
def test_delete_department_in_cascade_mode_removes_subtree(
    api_client,
    root_department,
):
    child = Department.objects.create(
        name='Child',
        parent=root_department,
    )
    Employee.objects.create(
        department=root_department,
        full_name='Root Employee',
        position='Lead',
    )
    Employee.objects.create(
        department=child,
        full_name='Child Employee',
        position='Engineer',
    )

    response = api_client.delete(
        f'/departments/{root_department.id}/?mode=cascade'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Department.objects.filter(pk=root_department.pk).exists()
    assert not Department.objects.filter(pk=child.pk).exists()
    assert Employee.objects.count() == 0


@pytest.mark.django_db
def test_delete_department_in_reassign_mode_keeps_subtree(
    api_client,
    source_department,
    child_department,
    target_department,
    source_employee,
    child_employee,
):
    response = api_client.delete(
        f'/departments/{source_department.id}/?mode=reassign'
        f'&reassign_to_department_id={target_department.id}'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Department.objects.filter(pk=source_department.pk).exists()
    assert Department.objects.filter(pk=child_department.pk).exists()

    child_department.refresh_from_db()
    source_employee.refresh_from_db()
    child_employee.refresh_from_db()

    assert child_department.parent_id == target_department.id
    assert source_employee.department_id == target_department.id
    assert child_employee.department_id == child_department.id
