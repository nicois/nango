# Generated by Django 4.0 on 2021-12-22 00:42
from typing import List
from typing import Tuple

import nango.models
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies: List[Tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("notes", models.TextField()),
            ],
            bases=(nango.models.LockableMixin, models.Model),
        ),
    ]
