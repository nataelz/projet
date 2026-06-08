from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("company/<int:company_id>", views.company, name="company"),
    path("processor/<int:processor_id>", views.processor, name="processor"),
    path("memory/<int:memory_id>", views.memory, name="memory"),
    path("storage/<int:storage_id>", views.storage, name="storage"),
    path("graphicscard/<int:graphicscard_id>", views.graphicscard, name="graphicscard"),
    path("network/<int:network_id>", views.network, name="network"),
    path("computer/<int:computer_id>", views.computer, name="computer"),
    path("search", views.search, name="search"),
]
