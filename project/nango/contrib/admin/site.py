from django.contrib.admin import site

from .admin import ModelAdmin


def register(model):
    """
    You can use this in place of admin.site.register
    with your nango-aware models
    """
    return site.register(model, ModelAdmin)
