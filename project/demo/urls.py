from django.urls import path

from . import views

app_name = "demo"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.UpdateView.as_view(), name="edit"),
    path("<int:pk>/delete", views.DeleteView.as_view(), name="delete"),
    path("new/", views.CreateView.as_view(), name="new"),
]
