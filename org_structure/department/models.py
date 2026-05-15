from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_department_parent_name",
            ),
        ]

    def __str__(self):
        return self.name


class Employee(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="employees",
    )
    full_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    hired_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.full_name
