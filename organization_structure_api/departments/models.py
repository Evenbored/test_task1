from django.db import models

from core.models import TimeStampedModel


# Create your models here.
class Department(TimeStampedModel):
    name = models.CharField(max_length=200, blank=False)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        ordering = ["created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_department_name_per_parent",
                nulls_distinct=False,
            ),
            models.CheckConstraint(
                condition=~models.Q(name=""),
                name="department_name_not_empty",
            ),
        ]

    def __str__(self) -> str:
        return self.name
