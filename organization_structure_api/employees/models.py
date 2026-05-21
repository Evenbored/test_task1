from django.db import models

from core.models import TimeStampedModel
# Create your models here.

class Employee(TimeStampedModel):
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.CASCADE,
        related_name='employees',
    )
    full_name = models.CharField(max_length=200, blank=False)
    position = models.CharField(max_length=200, blank=False)
    hired_at = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(full_name=""),
                name="employee_full_name_not_empty",
            ),
            models.CheckConstraint(
                condition=~models.Q(position=""),
                name="employee_position_not_empty",
            ),
        ]
    def __str__(self) -> str:
        return self.full_name