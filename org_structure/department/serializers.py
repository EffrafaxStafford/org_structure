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


class DepartmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'parent', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
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
    employees = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = (
            'id',
            'name',
            'created_at',
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
