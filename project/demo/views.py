from django.urls import reverse_lazy
from django.views.generic import ListView
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


class CreateView(edit.CreateView):
    model = Customer
    fields = ["name", "notes"]
    success_url = reverse_lazy("demo:index")


class DeleteView(edit.DeleteView):
    model = Customer
    success_url = reverse_lazy("demo:index")
