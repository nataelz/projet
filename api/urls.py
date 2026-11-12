from django.urls import path

from . import views

urlpatterns = [
    # --- PC ---------------------------------------------------------------
    path("pcs/", views.liste_pcs, name="api-pcs"),
    # Ces deux routes DOIVENT rester avant <slug:slug>, sinon elles seraient
    # interprétées comme des slugs de produit.
    path("pcs/comparer/", views.comparer_pcs, name="api-pcs-comparer"),
    path("pcs/meilleures-affaires/", views.meilleures_affaires, name="api-pcs-affaires"),
    path("pcs/<slug:slug>/", views.detail_pc, name="api-pc-detail"),
    path("pcs/<slug:slug>/offres/", views.offres_pc, name="api-pc-offres"),
    path("pcs/<slug:slug>/historique/", views.historique_pc, name="api-pc-historique"),
    # --- Référentiels / filtres -------------------------------------------
    path("marques/", views.liste_marques, name="api-marques"),
    path("marchands/", views.liste_marchands, name="api-marchands"),
    path("processeurs/", views.liste_processeurs, name="api-processeurs"),
    path("cartes-graphiques/", views.liste_cartes_graphiques, name="api-gpus"),
    path("filtres/", views.filtres_disponibles, name="api-filtres"),
]

