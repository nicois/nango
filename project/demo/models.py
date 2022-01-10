# Create your models here.
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

    def __str__(self) -> str:
        return self.name.title()

    class Meta:
        abstract = False
