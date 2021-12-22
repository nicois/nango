from django.contrib import admin
from nango.contrib.admin import ModelAdmin
from nango.contrib.admin import register
from nango.contrib.admin import TabularInline

from .models import Company
from .models import Customer

# from django.contrib.admin import TabularInline


class CustomerInline(TabularInline):
    model = Customer


@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    inlines = [CustomerInline]


register(Customer)
