# nango

## Installation

```bash
pip install nango
```

## Configuration

### Update views.py (if using generic model views)

Instead of using Django's generic views, replace them with nango's. You can safely just update the `import` statements
with nango. The appropriate views (e.g. UpdateView) will be modified, ensuring they use an "enhanced" form class, and the other views will also be available, unmodified.

```python
from django.urls import reverse_lazy
from nango.views.generic import ListView
from nango.views.generic import edit

from .models import Customer


class IndexView(ListView):
    template_name = "demo/index.html"
    context_object_name = "customers"

    def get_queryset(self):
        return Customer.objects.all()


class UpdateView(edit.UpdateView):
    model = Customer
    fields = ["name", "notes", "company"]
    prefix = "foo"

    def get_form(self):
        return super().get_form()

    def get_success_url(self):
        # return reverse_lazy("demo:edit", kwargs={"pk": self.object.id})
        return reverse_lazy("demo:index")
...
```

### Update forms.py (if explicitly creating forms)

Any forms you are making yourself will need a mixin added to it. You can either do this by explicitly adding the mixin,
or modifying the import of the Model base class.

```python
from django.forms import Form
from nango.forms import FormMixin

class MyForm(FormMixin, Form):
    ...
```

```python
from nango.forms import Form

class MyForm(Form):
    ...
```

### Update models.py

To make a model nango-aware, it will need a mixin added to it. You can either do this by explicitly adding the mixin,
or modifying the import of the Model base class.
If you choose the first option, you will also need to explicitly mark this
class as not abstract, as shown below:

```python
from django.db import models
from nango.db.models import TrackableMixin
class Customer(TrackableMixin, models.Model):
    class Meta:
        abstract = False
        ...
    ...
```

```python
from nango.db import models

class Customer(models.Model):
    ...
```

Django may prompt you to create migrations. If so, rest assured that these migrations will not actually modify anything in your database; they are only needed
as the model methods are different.

### Register the nango application

In your settings.py:

```python
...
INSTALLED_APPS = [
    "nango.apps.NangoConfig",
    "django.contrib.admin",
    ...
    ]
...
```

### Update admin.py

Simply change your `django.contrib` imports to `nango.contrib`. The rest of the module can be left unchanged. e.g.

```python
from nango.contrib import admin
from nango.contrib.admin import ModelAdmin
from nango.contrib.admin import register
from nango.contrib.admin import TabularInline

from .models import Company
from .models import Customer


class CustomerInline(TabularInline):
    model = Customer


@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    inlines = [CustomerInline]


admin.site.register(Customer)
```

## OK, so what is actually happening now I've enabled nango?

1. Whenever a form is rendered (including formsets), either in the admin panel or via a ModelForm, the HTML will include additional hidden input elements. These will ensure that when the form is POSTed, the server will not only be provided with the new field values, but also the original values.
2. When a form is POSTed, if the additional hidden items are present, these are provided to the associated model instance, prior to other form processing.
3. Nango's model mixin will provide additional checks, ensuring that the database currently holds the original values contained in the form. (By using select_for_update, we effectively lock these records in the database while performing this check, for the duration of the request).
4. If `clean()` fails, appropriate messages will be shown to the user, via the normal mechanism.
