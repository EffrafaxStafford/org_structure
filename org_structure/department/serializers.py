from rest_framework import serializers

from .models import Department, Employee


def _validate_department_name_uniqueness(serializer, attrs):
    """Проверяет, что в рамках одного parent нет двух подразделений с одинаковым названием."""

    instance = getattr(serializer, 'instance', None)
    parent = attrs.get(
        'parent',
        instance.parent if instance is not None else None,
    )
    name = attrs.get(
        'name',
        instance.name if instance is not None else None,
    )

    if name is None:
        return

    existing_departments = Department.objects.filter(
        parent=parent,
        name=name,
    )

    if instance is not None:
        existing_departments = existing_departments.exclude(pk=instance.pk)

    if existing_departments.exists():
        raise serializers.ValidationError({
            'name': 'Подразделение с таким названием уже существует в рамках этого parent.'
        })


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'parent', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        _validate_department_name_uniqueness(self, attrs)
        return attrs


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'department', 'full_name',
                  'position', 'hired_at', 'created_at')
        read_only_fields = ('id', 'department', 'created_at')


class DepartmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'parent', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        _validate_department_name_uniqueness(self, attrs)

        department = self.instance
        new_parent = attrs.get('parent', department.parent)

        if new_parent is None:
            return attrs

        if new_parent.id == department.id:
            raise serializers.ValidationError({
                'parent': 'Подразделение не может быть родителем самого себя.'
            })

        if self._is_descendant(
            possible_child=new_parent,
            possible_parent=department,
        ):
            raise serializers.ValidationError({
                'parent': 'Нельзя переместить подразделение внутрь своего поддерева.'
            })

        return attrs

    def _is_descendant(self, possible_child, possible_parent) -> bool:
        """Проверяет, является ли possible_child потомком possible_parent."""
        current = possible_child

        while current is not None:
            if current.id == possible_parent.id:
                return True

            current = current.parent

        return False


class DepartmentTreeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(source='*', read_only=True)
    employees = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = (
            'department',
            'employees',
            'children',
        )

    def get_employees(self, obj):
        include_employees = self.context.get(
            'include_employees',
            True,
        )

        if not include_employees:
            return []

        employees = obj.employees.all().order_by('full_name')

        return EmployeeSerializer(
            employees,
            many=True,
        ).data

    def get_children(self, obj):
        depth = self.context.get('depth', 1)

        if depth <= 0:
            return []

        children = obj.children.all()

        return DepartmentTreeSerializer(
            children,
            many=True,
            context={
                **self.context,
                'depth': depth - 1,
            }
        ).data
