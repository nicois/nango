# Create your models here.
from django.core.exceptions import ValidationError
from nango.db import models


class Company(models.Model):
    class Meta:
        verbose_name_plural = "companies"
        abstract = False

    name = models.CharField(max_length=100)
    notes = models.TextField()

    def __str__(self) -> str:
        return self.name.title()


class Customer(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField()
    company = models.ForeignKey(
        Company, null=True, default=None, on_delete=models.PROTECT
    )

    def clean(self):
        self.name = self.name.title()
        if len(self.name) < 5:
            raise ValidationError({"name": "Name is too short"})
        return super().clean()

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = False
