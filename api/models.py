"""
Modèles Django : comparateur de PC / meilleur prix multi-marchands.

Principe :
- ProduitPC  = fiche produit "canonique" (un seul enregistrement par modèle de PC)
- Marchand   = un site de vente (Amazon, LDLC, Boulanger...)
- Offre      = le prix d'un ProduitPC chez un Marchand
- HistoriquePrix = chaque variation de prix d'une Offre (graphiques, détection de bons plans)
- Processeur / CarteGraphique = tables de référence avec scores benchmark,
  pour comparer objectivement les performances.

Compatible Django 5.1+ (CheckConstraint(condition=...)).
Pour Django < 5.1, remplacer `condition=` par `check=`.
"""

from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import F, Min
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


# --------------------------------------------------------------------------
# Référentiels
# --------------------------------------------------------------------------
class Marque(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to="marques/", blank=True)

    class Meta:
        ordering = ["nom"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Processeur(models.Model):
    """Ex : Intel Core i7-13700H, AMD Ryzen 7 7840HS, Apple M3 Pro."""

    class Fabricant(models.TextChoices):
        INTEL = "intel", "Intel"
        AMD = "amd", "AMD"
        APPLE = "apple", "Apple"
        QUALCOMM = "qualcomm", "Qualcomm"
        AUTRE = "autre", "Autre"

    fabricant = models.CharField(max_length=20, choices=Fabricant.choices)
    modele = models.CharField("modèle", max_length=100, unique=True)
    nb_coeurs = models.PositiveSmallIntegerField("cœurs", null=True, blank=True)
    nb_threads = models.PositiveSmallIntegerField("threads", null=True, blank=True)
    frequence_max_ghz = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    score_benchmark = models.PositiveIntegerField(
        "score benchmark (ex. PassMark)",
        null=True,
        blank=True,
        help_text="Sert au calcul du score de performance global.",
    )

    class Meta:
        ordering = ["fabricant", "modele"]
        verbose_name = "processeur"

    def __str__(self):
        return self.modele


class CarteGraphique(models.Model):
    """Ex : NVIDIA RTX 4060 Laptop, AMD Radeon 780M, Intel Iris Xe (intégrée)."""

    class Fabricant(models.TextChoices):
        NVIDIA = "nvidia", "NVIDIA"
        AMD = "amd", "AMD"
        INTEL = "intel", "Intel"
        APPLE = "apple", "Apple"
        AUTRE = "autre", "Autre"

    fabricant = models.CharField(max_length=20, choices=Fabricant.choices)
    modele = models.CharField("modèle", max_length=100, unique=True)
    vram_go = models.PositiveSmallIntegerField("VRAM (Go)", null=True, blank=True)
    dediee = models.BooleanField("dédiée", default=False)
    score_benchmark = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["fabricant", "modele"]
        verbose_name = "carte graphique"
        verbose_name_plural = "cartes graphiques"

    def __str__(self):
        return self.modele


# --------------------------------------------------------------------------
# Produit
# --------------------------------------------------------------------------
class ProduitQuerySet(models.QuerySet):
    def avec_meilleur_prix(self):
        """Annote chaque produit avec le prix total minimum parmi les offres actives."""
        return self.annotate(
            meilleur_prix_annote=Min(
                F("offres__prix") + F("offres__frais_livraison"),
                filter=models.Q(
                    offres__actif=True,
                    offres__disponibilite__in=[
                        Offre.Disponibilite.EN_STOCK,
                        Offre.Disponibilite.LIMITE,
                    ],
                ),
            )
        )


class ProduitPC(models.Model):
    class TypePC(models.TextChoices):
        PORTABLE = "portable", "PC portable"
        FIXE = "fixe", "PC fixe / tour"
        TOUT_EN_UN = "aio", "Tout-en-un"
        MINI_PC = "mini", "Mini PC"

    class Usage(models.TextChoices):
        BUREAUTIQUE = "bureautique", "Bureautique"
        GAMING = "gaming", "Gaming"
        CREATION = "creation", "Création / Pro"
        ULTRAPORTABLE = "ultraportable", "Ultraportable"
        POLYVALENT = "polyvalent", "Polyvalent"

    class TypeStockage(models.TextChoices):
        SSD = "ssd", "SSD"
        HDD = "hdd", "HDD"
        EMMC = "emmc", "eMMC"
        HYBRIDE = "hybride", "SSD + HDD"

    # Identité
    marque = models.ForeignKey(Marque, on_delete=models.PROTECT, related_name="produits")
    nom = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    type_pc = models.CharField(max_length=10, choices=TypePC.choices, default=TypePC.PORTABLE)
    usage = models.CharField(max_length=20, choices=Usage.choices, default=Usage.POLYVALENT)

    # Identifiants permettant de fusionner les offres de marchands différents
    reference_fabricant = models.CharField(
        "référence fabricant (MPN)", max_length=100, blank=True, db_index=True
    )
    ean = models.CharField("EAN / GTIN", max_length=14, blank=True, db_index=True)

    # Caractéristiques techniques
    processeur = models.ForeignKey(
        Processeur, on_delete=models.PROTECT, null=True, blank=True, related_name="produits"
    )
    carte_graphique = models.ForeignKey(
        CarteGraphique, on_delete=models.PROTECT, null=True, blank=True, related_name="produits"
    )
    ram_go = models.PositiveSmallIntegerField("RAM (Go)", null=True, blank=True)
    type_ram = models.CharField(max_length=10, blank=True, help_text="DDR4, DDR5, LPDDR5...")
    stockage_go = models.PositiveIntegerField("stockage (Go)", null=True, blank=True)
    type_stockage = models.CharField(
        max_length=10, choices=TypeStockage.choices, default=TypeStockage.SSD, blank=True
    )
    taille_ecran_pouces = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    resolution_ecran = models.CharField(max_length=20, blank=True, help_text="Ex : 1920x1080")
    frequence_ecran_hz = models.PositiveSmallIntegerField(null=True, blank=True)
    systeme_exploitation = models.CharField("système d'exploitation", max_length=50, blank=True)
    poids_kg = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    autonomie_heures = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    caracteristiques_extra = models.JSONField(
        default=dict,
        blank=True,
        help_text="Ports, Wi-Fi, clavier, etc. Tout ce qui ne mérite pas une colonne.",
    )

    # Présentation
    image = models.ImageField(upload_to="produits/", blank=True)
    description = models.TextField(blank=True)

    # Score calculé (voir calculer_score_performance)
    score_performance = models.PositiveIntegerField(
        null=True, blank=True, editable=False, db_index=True
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    objects = ProduitQuerySet.as_manager()

    class Meta:
        ordering = ["marque__nom", "nom"]
        verbose_name = "produit PC"
        verbose_name_plural = "produits PC"
        indexes = [
            models.Index(fields=["type_pc", "usage"]),
            models.Index(fields=["ram_go", "stockage_go"]),
        ]

    def __str__(self):
        return f"{self.marque} {self.nom}"

    def get_absolute_url(self):
        return reverse("produit_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.marque.nom} {self.nom}")[:260]
            slug, i = base, 2
            while ProduitPC.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        self.score_performance = self.calculer_score_performance()
        super().save(*args, **kwargs)

    # -- Performance / prix ------------------------------------------------
    def calculer_score_performance(self):
        """
        Score simple et ajustable : CPU + GPU (benchmarks) + bonus RAM / stockage.
        À adapter selon vos besoins (pondérations par usage, etc.).
        """
        cpu = self.processeur.score_benchmark if self.processeur_id else None
        gpu = self.carte_graphique.score_benchmark if self.carte_graphique_id else None
        if cpu is None and gpu is None:
            return None
        score = (cpu or 0) * 0.5 + (gpu or 0) * 0.35
        score += (self.ram_go or 0) * 40
        score += min((self.stockage_go or 0), 4000) * 0.2
        return int(score)

    def offres_actives(self):
        return self.offres.filter(
            actif=True,
            disponibilite__in=[Offre.Disponibilite.EN_STOCK, Offre.Disponibilite.LIMITE],
        ).select_related("marchand")

    @property
    def meilleure_offre(self):
        """Offre au prix total (livraison comprise) le plus bas."""
        offres = list(self.offres_actives())
        return min(offres, key=lambda o: o.prix_total) if offres else None

    @property
    def meilleur_prix(self):
        offre = self.meilleure_offre
        return offre.prix_total if offre else None

    @property
    def rapport_qualite_prix(self):
        """Points de performance par euro : plus c'est haut, mieux c'est."""
        prix = self.meilleur_prix
        if not prix or not self.score_performance:
            return None
        return round(Decimal(self.score_performance) / prix, 2)


# --------------------------------------------------------------------------
# Marchands & offres
# --------------------------------------------------------------------------
class Marchand(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    site_web = models.URLField()
    logo = models.ImageField(upload_to="marchands/", blank=True)
    actif = models.BooleanField(default=True)

    # Livraison par défaut (utilisée quand l'offre n'a pas de frais précis)
    frais_livraison_defaut = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
    )
    livraison_gratuite_des = models.DecimalField(
        "livraison gratuite dès (€)", max_digits=8, decimal_places=2,
        null=True, blank=True,
    )
    delai_livraison_jours = models.PositiveSmallIntegerField(null=True, blank=True)

    # Réputation
    note_fiabilite = models.DecimalField(
        "note de fiabilité (0-5)", max_digits=2, decimal_places=1, null=True, blank=True
    )

    # Monétisation / collecte des prix
    modele_affiliation = models.CharField(
        max_length=255, blank=True,
        help_text="Gabarit d'URL d'affiliation, ex : https://.../?url={url}&aff=XXXX",
    )
    source_donnees = models.CharField(
        max_length=20,
        choices=[("flux", "Flux produits (CSV/XML)"), ("api", "API"), ("scraping", "Scraping")],
        default="flux",
    )
    derniere_synchro = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "marchand"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    def url_affiliee(self, url_produit):
        if self.modele_affiliation:
            return self.modele_affiliation.format(url=url_produit)
        return url_produit


class Offre(models.Model):
    class Disponibilite(models.TextChoices):
        EN_STOCK = "en_stock", "En stock"
        LIMITE = "limite", "Stock limité"
        PRECOMMANDE = "precommande", "Précommande"
        RUPTURE = "rupture", "Rupture de stock"

    class Etat(models.TextChoices):
        NEUF = "neuf", "Neuf"
        RECONDITIONNE = "reconditionne", "Reconditionné"
        OCCASION = "occasion", "Occasion"

    produit = models.ForeignKey(ProduitPC, on_delete=models.CASCADE, related_name="offres")
    marchand = models.ForeignKey(Marchand, on_delete=models.CASCADE, related_name="offres")
    sku_marchand = models.CharField(
        "identifiant chez le marchand", max_length=100, blank=True
    )
    url = models.URLField(max_length=1000)

    prix = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    prix_barre = models.DecimalField(
        "ancien prix", max_digits=9, decimal_places=2, null=True, blank=True
    )
    frais_livraison = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
    )
    devise = models.CharField(max_length=3, default="EUR")

    etat = models.CharField(max_length=15, choices=Etat.choices, default=Etat.NEUF)
    disponibilite = models.CharField(
        max_length=15, choices=Disponibilite.choices, default=Disponibilite.EN_STOCK
    )
    garantie_mois = models.PositiveSmallIntegerField(null=True, blank=True)

    actif = models.BooleanField(default=True)
    derniere_verification = models.DateTimeField(default=timezone.now)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["prix"]
        constraints = [
            models.UniqueConstraint(
                fields=["produit", "marchand", "etat"], name="offre_unique_par_marchand_etat"
            ),
            models.CheckConstraint(condition=models.Q(prix__gt=0), name="offre_prix_positif"),
        ]
        indexes = [
            models.Index(fields=["produit", "actif", "prix"]),
            models.Index(fields=["derniere_verification"]),
        ]

    def __str__(self):
        return f"{self.produit} @ {self.marchand} : {self.prix} €"

    @property
    def prix_total(self):
        return self.prix + self.frais_livraison

    @property
    def remise_pourcentage(self):
        if self.prix_barre and self.prix_barre > self.prix:
            return int((self.prix_barre - self.prix) / self.prix_barre * 100)
        return 0

    @property
    def url_affiliee(self):
        return self.marchand.url_affiliee(self.url)

    @property
    def est_a_jour(self):
        """Offre vérifiée dans les dernières 48 h."""
        return timezone.now() - self.derniere_verification < timedelta(hours=48)

    def save(self, *args, **kwargs):
        """Enregistre un point d'historique à la création et à chaque changement de prix."""
        with transaction.atomic():
            ancien_prix = None
            if self.pk:
                ancien_prix = (
                    Offre.objects.filter(pk=self.pk).values_list("prix", flat=True).first()
                )
            super().save(*args, **kwargs)
            if ancien_prix is None or ancien_prix != self.prix:
                HistoriquePrix.objects.create(
                    offre=self, prix=self.prix, frais_livraison=self.frais_livraison
                )


class HistoriquePrix(models.Model):
    offre = models.ForeignKey(Offre, on_delete=models.CASCADE, related_name="historique")
    prix = models.DecimalField(max_digits=9, decimal_places=2)
    frais_livraison = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    releve_le = models.DateTimeField("relevé le", default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-releve_le"]
        verbose_name = "historique de prix"
        verbose_name_plural = "historiques de prix"
        indexes = [models.Index(fields=["offre", "-releve_le"])]

    def __str__(self):
        return f"{self.offre_id} : {self.prix} € le {self.releve_le:%d/%m/%Y}"


# --------------------------------------------------------------------------
# Utilisateurs : favoris & alertes
# --------------------------------------------------------------------------
class Favori(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favoris"
    )
    produit = models.ForeignKey(ProduitPC, on_delete=models.CASCADE, related_name="favoris")
    ajoute_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["utilisateur", "produit"], name="favori_unique")
        ]
        ordering = ["-ajoute_le"]

    def __str__(self):
        return f"{self.utilisateur} ♥ {self.produit}"


class AlertePrix(models.Model):
    """Prévient l'utilisateur quand le meilleur prix passe sous son seuil."""

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="alertes_prix"
    )
    produit = models.ForeignKey(ProduitPC, on_delete=models.CASCADE, related_name="alertes")
    prix_cible = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    active = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    derniere_notification = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["utilisateur", "produit"], name="alerte_unique_par_produit"
            )
        ]
        verbose_name = "alerte de prix"
        verbose_name_plural = "alertes de prix"

    def __str__(self):
        return f"{self.utilisateur} : {self.produit} < {self.prix_cible} €"

    def est_declenchee(self):
        prix = self.produit.meilleur_prix
        return self.active and prix is not None and prix <= self.prix_cible