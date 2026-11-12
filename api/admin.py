from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register([Marque, Processeur, Marchand, Offre, CarteGraphique, HistoriquePrix, ProduitPC])
