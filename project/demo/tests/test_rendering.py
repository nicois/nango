from pprint import pprint

from bs4 import BeautifulSoup
from demo.models import Customer
from nango.forms import ModelForm
from nango.forms import modelformset_factory
from pytest import mark

"""
Tests verifying that form fields
are rendered correctly, in that
they include the hidden inputs
to provide original values back
to django when the form is submitted
"""


def instantiate_formset(formset_class, data, **kw):
    prefix = formset_class().prefix
    formset_data = {}
    for i, form_data in enumerate(data):
        for name, value in form_data.items():
            if isinstance(value, list):
                for j, inner in enumerate(value):
                    formset_data["{}-{}-{}_{}".format(prefix, i, name, j)] = inner
            else:
                formset_data["{}-{}-{}".format(prefix, i, name)] = value
    formset_data[f"{prefix}-TOTAL_FORMS"] = len(data)
    formset_data[f"{prefix}-INITIAL_FORMS"] = 0
    pprint(formset_data)
    return formset_class(formset_data, **kw)


# Create the form class.
class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "notes", "company"]


@mark.django_db
def test_update_form():
    customer = Customer.objects.create(name="foo")
    form = CustomerForm(instance=customer)
    content = form.render()
    soup = BeautifulSoup(content, "html.parser")
    eles = soup.find_all("input", {"data-model-name": "customer"})
    for ele, field_name in zip(eles, ["name", "notes", "company"]):
        assert ele["data-app-label"] == "demo"
        assert ele["data-instance-pk"] == "1"
        assert ele["data-model-name"] == "customer"
        assert ele["data-original-name"] == field_name
        assert ele["data-related-form-id"] == f"id_{field_name}"
        assert ele["name"] == f"__original-{field_name}"


@mark.django_db
def test_update_formset():
    foo = Customer.objects.create(name="foo")
    bar = Customer.objects.create(name="bar")
    baz = Customer.objects.create(name="baz")
    CustomerFormset = modelformset_factory(
        Customer, fields=["name", "notes", "company"]
    )
    formset = CustomerFormset(queryset=Customer.objects.filter(name__startswith="b"))
    content = formset.render()
    soup = BeautifulSoup(content, "html.parser")

    for form_index, (customer, selector) in enumerate(
        [
            (bar, {"data-instance-pk": "2"}),
            (baz, {"data-instance-pk": "3"}),
        ]
    ):
        eles = soup.find_all("input", selector)
        pprint(eles)
        for ele, field_name in zip(eles, ["name", "notes", "company"]):
            assert ele["data-app-label"] == "demo"
            assert ele["data-instance-pk"] == str(customer.pk)
            assert ele["data-model-name"] == "customer"
            assert ele["data-original-name"] == field_name
            assert ele["data-related-form-id"] == f"id_form-{form_index}-{field_name}"
            assert ele["name"] == f"__original-form-{form_index}-{field_name}"
