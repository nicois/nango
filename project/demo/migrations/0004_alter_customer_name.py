# Generated by Django 4.0.1 on 2022-02-12 23:16
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("demo", "0003_alter_company_options_alter_customer_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="name",
            field=models.CharField(max_length=100),
        ),
    ]
