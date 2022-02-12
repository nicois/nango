# nango

Streamlining Django forms to provide all the wins of single-page-applications without the pain.

## Key features

Available to all Django deployments:

- Django forms no longer silently overwrite changes made in parallel by other users

Available if Django Channels is enabled:

- Django forms can receive push notifications from the server (via Channels) when data used on the form changes, rather than only discovering data is out-of-date when the form is submitted
- Django forms can send provisional form data to the server, allowing server-based field validation before the form is submitted
- Django forms can save form data as it is edited, without needing a "submit" button.

## What do all Django apps get?

Out of the box, Django provides reasonable support for database-level data consistency while a request is being processed, thanks to
transactions. However, it is let down by not providing an easy way to avoid data corruptions between requests.

A simple example, where two users edit the same customer using the admin panel.

https://user-images.githubusercontent.com/236562/148663962-8f343216-cced-41fc-b2c0-c99ccda524e2.mp4

https://user-images.githubusercontent.com/236562/148663959-a0b69f19-c91d-405d-a4cc-1316a24c4bb8.mp4

As you can see, using the normal django tooling, the change made by the first user is lost. This occurs because Django
does not track the original form value, making it impossible for it to know that the data was modified between when
the form was rendered, and when the form was submitted.


### Does this matter to me?

Here's a simple checklist to help you consider if this is a problem for you.

- Can the same model be edited on multiple forms?
- Can the same form be accessed simultaneously by multiple people?
- Can one user access the same form in multiple tabs/windows, either on the same or different devices?

If the data you're storing is not important, maybe you can get away without caring about these "edge cases". However,
if they do occur, you will have lost user data. There will be no errors, just users complaining that the changes they
made were not saved. The original data will be irretrievable, and it will be difficult to even work out how often it is occurring.

[learn more](./nango-all.md)

## What do Django Channels-enabled apps get?
Here is a quick example, where a model is being simultaneous edited in two admin panels, and two UpdateViews.
Things to note:
- the Customer model has a clean() rule ensuring the name and comment values are at least 5 characters long and there is a vowel in each word. Additionally it with capitalise the first letter in each word.
- the only additional changes required are enabling the auto-clean and auto-submit features in the UpdateView's definition:
```python
class UpdateView(edit.UpdateView):
    model = Customer
    fields = ["name", "notes", "company"]
    auto_clean_fields = ["name"]
    auto_submit_fields = ["notes"]
    ...
```

https://user-images.githubusercontent.com/236562/153730557-a22b473a-1680-465d-a898-1a7fa72e919f.mp4

Features demonstrated above:
- the admin panel views automatically reflect changes as they occur. If a conflict occurs (due to also changing a field's value locally), it is highlighted and cannot be successfully saved.
- the 'name' field, which is set to auto-clean, uses CSS to provide feedback on whether the current field value is valid, according to the server. In addition, if the field is not valid, the validation errors are shown. In both the admin panels and UpdateViews, any corrections to the field (ie: capitalisation) are reflected in realtime.
- the 'notes' field is set to auto-submit, meaning that whenever its value is changed, the change is sent via a websocket to the server, and if clean() is successful, the value is saved. CSS classes are also used to indicate the status of the field, such as failing validation, save in progress, or saved.

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
