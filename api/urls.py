from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("computer/<int:computer_id>", views.computer, name="computer"),
    path("search", views.search, name="search"),
]
