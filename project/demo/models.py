# Create your models here.
from django.db import models
from nango.models import LockableMixin
from nango.models import TrackableMixin


class Company(TrackableMixin, LockableMixin, models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField()

    def __str__(self) -> str:
        return self.name.title()

    class Meta:
        abstract = False


class Customer(TrackableMixin, LockableMixin, models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField()
    company = models.ForeignKey(
        Company, null=True, default=None, on_delete=models.PROTECT
    )

    def __str__(self) -> str:
        return self.name.title()

    class Meta:
        abstract = False
