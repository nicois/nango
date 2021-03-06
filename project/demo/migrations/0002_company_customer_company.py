# Generated by Django 4.0 on 2021-12-28 23:10
import django.db.models.deletion
import nango.db.models
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("demo", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Company",
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
            options={
                "abstract": False,
            },
            bases=(
                nango.db.models.TrackableMixin,
                nango.db.models.LockableMixin,
                models.Model,
            ),
        ),
        migrations.AddField(
            model_name="customer",
            name="company",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="demo.company",
            ),
        ),
    ]
