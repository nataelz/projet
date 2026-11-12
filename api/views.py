"""
Vues JSON pour rechercher dans les PC (Django pur, sans Django REST Framework).

Toutes les vues sont en lecture seule (GET) et renvoient du JSON.
Les erreurs ont toujours la forme : {"erreur": "message"}.
"""

from datetime import timedelta
from decimal import Decimal, InvalidOperation
from functools import wraps

from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, F, FloatField, Max, Min, Prefetch, Q
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import (
    CarteGraphique,
    HistoriquePrix,
    Marchand,
    Marque,
    Offre,
    ProduitPC,
    Processeur,
)

DISPONIBLES = [Offre.Disponibilite.EN_STOCK, Offre.Disponibilite.LIMITE]
TAILLE_PAGE_DEFAUT = 20
TAILLE_PAGE_MAX = 100
MAX_COMPARAISON = 4


# --------------------------------------------------------------------------
# Utilitaires : erreurs, réponses, lecture des paramètres
# --------------------------------------------------------------------------
class ParamError(Exception):
    """Paramètre de requête invalide (HTTP 400)."""


class NotFound(Exception):
    """Ressource introuvable (HTTP 404)."""


def reponse(data, status=200):
    return JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": False})


def erreur(message, status):
    return reponse({"erreur": message}, status=status)


def api(view):
    """GET uniquement + conversion des exceptions métier en réponses JSON."""

    @require_GET
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except ParamError as exc:
            return erreur(str(exc), 400)
        except NotFound as exc:
            return erreur(str(exc), 404)

    return wrapper


def num(valeur):
    """Decimal -> float (plus pratique côté front) ; None reste None."""
    return float(valeur) if valeur is not None else None


def _texte(request, nom):
    return (request.GET.get(nom) or "").strip()


def _liste(request, nom):
    """Accepte ?marque=asus,hp  ou  ?marque=asus&marque=hp."""
    valeurs = []
    for brut in request.GET.getlist(nom):
        valeurs.extend(v.strip() for v in brut.split(",") if v.strip())
    return valeurs


def _entier(request, nom, defaut=None, mini=None, maxi=None):
    brut = _texte(request, nom)
    if not brut:
        return defaut
    try:
        valeur = int(brut)
    except ValueError:
        raise ParamError(f"Paramètre '{nom}' invalide : entier attendu.")
    if mini is not None and valeur < mini:
        raise ParamError(f"Paramètre '{nom}' doit être >= {mini}.")
    if maxi is not None and valeur > maxi:
        raise ParamError(f"Paramètre '{nom}' doit être <= {maxi}.")
    return valeur


def _decimal(request, nom):
    brut = _texte(request, nom).replace(",", ".")
    if not brut:
        return None
    try:
        return Decimal(brut)
    except InvalidOperation:
        raise ParamError(f"Paramètre '{nom}' invalide : nombre attendu.")


def _bool(request, nom):
    brut = _texte(request, nom).lower()
    if not brut:
        return None
    if brut in ("1", "true", "oui", "yes"):
        return True
    if brut in ("0", "false", "non", "no"):
        return False
    raise ParamError(f"Paramètre '{nom}' invalide : booléen attendu (true/false).")


def _choix(request, nom, valeurs_valides):
    valeurs = _liste(request, nom)
    invalides = [v for v in valeurs if v not in valeurs_valides]
    if invalides:
        raise ParamError(
            f"Valeur(s) invalide(s) pour '{nom}' : {', '.join(invalides)}. "
            f"Valeurs possibles : {', '.join(sorted(valeurs_valides))}."
        )
    return valeurs


# --------------------------------------------------------------------------
# Sérialisation
# --------------------------------------------------------------------------
def offre_dict(offre):
    marchand = offre.marchand
    return {
        "id": offre.id,
        "marchand": {
            "nom": marchand.nom,
            "slug": marchand.slug,
            "note_fiabilite": num(marchand.note_fiabilite),
        },
        "prix": num(offre.prix),
        "prix_barre": num(offre.prix_barre),
        "remise_pourcentage": offre.remise_pourcentage,
        "frais_livraison": num(offre.frais_livraison),
        "prix_total": num(offre.prix_total),
        "etat": offre.etat,
        "disponibilite": offre.disponibilite,
        "garantie_mois": offre.garantie_mois,
        "url": offre.url_affiliee,
        "derniere_verification": offre.derniere_verification.isoformat(),
    }


def specs_dict(p):
    cpu, gpu = p.processeur, p.carte_graphique
    return {
        "processeur": cpu.modele if cpu else None,
        "carte_graphique": gpu.modele if gpu else None,
        "gpu_dediee": gpu.dediee if gpu else None,
        "ram_go": p.ram_go,
        "type_ram": p.type_ram or None,
        "stockage_go": p.stockage_go,
        "type_stockage": p.type_stockage or None,
        "ecran_pouces": num(p.taille_ecran_pouces),
        "resolution": p.resolution_ecran or None,
        "frequence_ecran_hz": p.frequence_ecran_hz,
        "systeme_exploitation": p.systeme_exploitation or None,
        "poids_kg": num(p.poids_kg),
        "autonomie_heures": num(p.autonomie_heures),
    }


def produit_resume(p, request):
    return {
        "slug": p.slug,
        "nom": p.nom,
        "marque": {"nom": p.marque.nom, "slug": p.marque.slug},
        "image": request.build_absolute_uri(p.image.url) if p.image else None,
    }


def produit_dict(p, request, detail=False):
    offres = sorted(p.offres_dispo, key=lambda o: o.prix_total)
    meilleure = offres[0] if offres else None
    rqp = None
    if meilleure and p.score_performance:
        rqp = round(p.score_performance / float(meilleure.prix_total), 2)

    data = {
        **produit_resume(p, request),
        "type": p.type_pc,
        "type_libelle": p.get_type_pc_display(),
        "usage": p.usage,
        "usage_libelle": p.get_usage_display(),
        "reference_fabricant": p.reference_fabricant or None,
        "ean": p.ean or None,
        "specs": specs_dict(p),
        "score_performance": p.score_performance,
        "rapport_qualite_prix": rqp,
        "meilleure_offre": offre_dict(meilleure) if meilleure else None,
        "nb_offres": len(offres),
    }
    if detail:
        data["description"] = p.description
        data["caracteristiques_extra"] = p.caracteristiques_extra
        data["offres"] = [offre_dict(o) for o in offres]
    return data


def lien_page(request, numero):
    params = request.GET.copy()
    params["page"] = numero
    return request.build_absolute_uri(f"{request.path}?{params.urlencode()}")


def paginer(request, queryset, serialiseur):
    taille = _entier(request, "page_size", TAILLE_PAGE_DEFAUT, 1, TAILLE_PAGE_MAX)
    numero = _entier(request, "page", 1, 1)
    paginator = Paginator(queryset, taille)
    try:
        page = paginator.page(numero)
    except EmptyPage:
        raise ParamError(f"Page hors limites (1 à {paginator.num_pages}).")
    return {
        "count": paginator.count,
        "page": page.number,
        "page_size": taille,
        "total_pages": paginator.num_pages,
        "next": lien_page(request, page.next_page_number()) if page.has_next() else None,
        "previous": lien_page(request, page.previous_page_number())
        if page.has_previous()
        else None,
        "results": [serialiseur(obj) for obj in page.object_list],
    }


# --------------------------------------------------------------------------
# Construction des querysets
# --------------------------------------------------------------------------
def offre_filtres(request=None):
    """
    Filtres appliqués aux OFFRES (disponibles + éventuellement marchand / état).
    Ils servent à la fois pour calculer le meilleur prix et pour les offres affichées,
    afin que les deux restent cohérents.
    """
    filtres = {"actif": True, "disponibilite__in": DISPONIBLES}
    if request is not None:
        marchands = _liste(request, "marchand")
        if marchands:
            filtres["marchand__slug__in"] = marchands
        etats = _choix(request, "etat", set(Offre.Etat.values))
        if etats:
            filtres["etat__in"] = etats
    return filtres


def produits_base(request=None):
    filtres = offre_filtres(request)
    q_offres = Q(**{f"offres__{k}": v for k, v in filtres.items()})
    return (
        ProduitPC.objects.select_related("marque", "processeur", "carte_graphique")
        # NB : "prix_mini" et non "meilleur_prix", déjà utilisé par une property du modèle.
        .annotate(prix_mini=Min(F("offres__prix") + F("offres__frais_livraison"), filter=q_offres))
        .filter(prix_mini__isnull=False)  # on n'affiche que les PC avec au moins une offre
        .prefetch_related(
            Prefetch(
                "offres",
                queryset=Offre.objects.filter(**filtres).select_related("marchand"),
                to_attr="offres_dispo",
            )
        )
    )


TRIS = {
    "prix": ["prix_mini"],
    "-prix": ["-prix_mini"],
    "performance": [F("score_performance").desc(nulls_last=True)],
    "qualite_prix": [F("rapport_qp").desc(nulls_last=True)],
    "recent": ["-cree_le"],
    "nom": ["marque__nom", "nom"],
}


def filtrer_produits(request):
    qs = produits_base(request)

    # Recherche texte : chaque mot doit apparaître quelque part
    for mot in _texte(request, "q").split():
        qs = qs.filter(
            Q(nom__icontains=mot)
            | Q(marque__nom__icontains=mot)
            | Q(reference_fabricant__icontains=mot)
            | Q(ean__icontains=mot)
            | Q(processeur__modele__icontains=mot)
            | Q(carte_graphique__modele__icontains=mot)
        )

    marques = _liste(request, "marque")
    if marques:
        qs = qs.filter(marque__slug__in=marques)

    types = _choix(request, "type", set(ProduitPC.TypePC.values))
    if types:
        qs = qs.filter(type_pc__in=types)

    usages = _choix(request, "usage", set(ProduitPC.Usage.values))
    if usages:
        qs = qs.filter(usage__in=usages)

    if _texte(request, "cpu"):
        qs = qs.filter(processeur__modele__icontains=_texte(request, "cpu"))
    if _texte(request, "gpu"):
        qs = qs.filter(carte_graphique__modele__icontains=_texte(request, "gpu"))
    dediee = _bool(request, "gpu_dediee")
    if dediee is not None:
        qs = qs.filter(carte_graphique__dediee=dediee)

    bornes = [
        ("ram_min", "ram_go__gte", _entier(request, "ram_min", mini=0)),
        ("ram_max", "ram_go__lte", _entier(request, "ram_max", mini=0)),
        ("stockage_min", "stockage_go__gte", _entier(request, "stockage_min", mini=0)),
        ("ecran_min", "taille_ecran_pouces__gte", _decimal(request, "ecran_min")),
        ("ecran_max", "taille_ecran_pouces__lte", _decimal(request, "ecran_max")),
        ("poids_max", "poids_kg__lte", _decimal(request, "poids_max")),
        ("autonomie_min", "autonomie_heures__gte", _decimal(request, "autonomie_min")),
        ("prix_min", "prix_mini__gte", _decimal(request, "prix_min")),
        ("prix_max", "prix_mini__lte", _decimal(request, "prix_max")),
    ]
    for _nom, critere, valeur in bornes:
        if valeur is not None:
            qs = qs.filter(**{critere: valeur})

    tri = _texte(request, "tri") or "prix"
    if tri not in TRIS:
        raise ParamError(f"Tri invalide. Valeurs possibles : {', '.join(TRIS)}.")
    if tri == "qualite_prix":
        qs = qs.annotate(
            rapport_qp=Cast("score_performance", FloatField())
            / Cast("prix_mini", FloatField())
        )
    return qs.order_by(*TRIS[tri], "pk")


def charger_produit(slug):
    produit = produits_base().filter(slug=slug).first()
    if produit is None:
        raise NotFound(f"Aucun PC avec le slug '{slug}' (ou aucune offre disponible).")
    return produit


# --------------------------------------------------------------------------
# Endpoints : PC
# --------------------------------------------------------------------------
@api
def liste_pcs(request):
    """GET /api/pcs/ : recherche, filtres, tri, pagination."""
    qs = filtrer_produits(request)
    return reponse(paginer(request, qs, lambda p: produit_dict(p, request)))


@api
def detail_pc(request, slug):
    """GET /api/pcs/<slug>/ : fiche complète avec toutes les offres."""
    return reponse(produit_dict(charger_produit(slug), request, detail=True))


@api
def offres_pc(request, slug):
    """GET /api/pcs/<slug>/offres/ : offres triées par prix total."""
    produit = charger_produit(slug)
    offres = sorted(produit.offres_dispo, key=lambda o: o.prix_total)
    return reponse(
        {
            "produit": produit_resume(produit, request),
            "count": len(offres),
            "results": [offre_dict(o) for o in offres],
        }
    )


@api
def historique_pc(request, slug):
    """GET /api/pcs/<slug>/historique/?jours=90&marchand=ldlc

    NB : un point est enregistré à chaque *changement* de prix ;
    entre deux points, le prix est constant (à tracer en escalier).
    """
    produit = charger_produit(slug)
    jours = _entier(request, "jours", 90, 1, 730)
    depuis = timezone.now() - timedelta(days=jours)

    points = HistoriquePrix.objects.filter(
        offre__produit=produit, releve_le__gte=depuis
    ).select_related("offre__marchand")
    marchands = _liste(request, "marchand")
    if marchands:
        points = points.filter(offre__marchand__slug__in=marchands)

    series = {}
    for h in points.order_by("releve_le"):
        serie = series.setdefault(
            h.offre_id,
            {
                "offre_id": h.offre_id,
                "marchand": {"nom": h.offre.marchand.nom, "slug": h.offre.marchand.slug},
                "etat": h.offre.etat,
                "points": [],
            },
        )
        serie["points"].append(
            {
                "date": h.releve_le.isoformat(),
                "prix": num(h.prix),
                "prix_total": num(h.prix + h.frais_livraison),
            }
        )

    tous = [pt["prix_total"] for s in series.values() for pt in s["points"]]
    return reponse(
        {
            "produit": produit_resume(produit, request),
            "jours": jours,
            "prix_total_min": min(tous) if tous else None,
            "prix_total_max": max(tous) if tous else None,
            "series": list(series.values()),
        }
    )


@api
def comparer_pcs(request):
    """GET /api/pcs/comparer/?slugs=a,b,c : jusqu'à 4 PC côte à côte."""
    slugs = _liste(request, "slugs")
    if len(slugs) < 2:
        raise ParamError("Fournissez au moins 2 slugs : ?slugs=slug1,slug2")
    if len(slugs) > MAX_COMPARAISON:
        raise ParamError(f"Maximum {MAX_COMPARAISON} PC comparables à la fois.")

    par_slug = {p.slug: p for p in produits_base().filter(slug__in=slugs)}
    manquants = [s for s in slugs if s not in par_slug]
    if manquants:
        raise NotFound(f"PC introuvable(s) : {', '.join(manquants)}")

    resultats = [produit_dict(par_slug[s], request) for s in slugs]
    return reponse({"count": len(resultats), "results": resultats})


@api
def meilleures_affaires(request):
    """GET /api/pcs/meilleures-affaires/?remise_min=15&limit=20 : plus grosses remises."""
    remise_min = _entier(request, "remise_min", 10, 1, 90)
    limite = _entier(request, "limit", 20, 1, 100)

    offres = (
        Offre.objects.filter(
            actif=True, disponibilite__in=DISPONIBLES, prix_barre__gt=F("prix")
        )
        .select_related("marchand", "produit__marque")
        .annotate(
            ratio_remise=Cast(F("prix_barre") - F("prix"), FloatField())
            / Cast("prix_barre", FloatField())
        )
        .filter(ratio_remise__gte=remise_min / 100)
        .order_by("-ratio_remise", "pk")[:limite]
    )
    resultats = [
        {**offre_dict(o), "produit": produit_resume(o.produit, request)} for o in offres
    ]
    return reponse({"count": len(resultats), "results": resultats})


# --------------------------------------------------------------------------
# Endpoints : référentiels & filtres
# --------------------------------------------------------------------------
@api
def liste_marques(request):
    """GET /api/marques/ : marques avec leur nombre de PC."""
    marques = Marque.objects.annotate(nb_produits=Count("produits")).order_by("nom")
    return reponse(
        {
            "results": [
                {"nom": m.nom, "slug": m.slug, "nb_produits": m.nb_produits}
                for m in marques
            ]
        }
    )


@api
def liste_marchands(request):
    """GET /api/marchands/ : sites comparés."""
    marchands = Marchand.objects.filter(actif=True).annotate(
        nb_offres=Count("offres", filter=Q(offres__actif=True))
    )
    return reponse(
        {
            "results": [
                {
                    "nom": m.nom,
                    "slug": m.slug,
                    "site_web": m.site_web,
                    "frais_livraison_defaut": num(m.frais_livraison_defaut),
                    "livraison_gratuite_des": num(m.livraison_gratuite_des),
                    "delai_livraison_jours": m.delai_livraison_jours,
                    "note_fiabilite": num(m.note_fiabilite),
                    "nb_offres": m.nb_offres,
                }
                for m in marchands
            ]
        }
    )


def _liste_composants(request, modele):
    qs = modele.objects.all()
    if _texte(request, "q"):
        qs = qs.filter(modele__icontains=_texte(request, "q"))
    return qs.order_by("fabricant", "modele")[:200]


@api
def liste_processeurs(request):
    """GET /api/processeurs/?q=ryzen : pour l'autocomplétion."""
    return reponse(
        {
            "results": [
                {
                    "modele": c.modele,
                    "fabricant": c.fabricant,
                    "nb_coeurs": c.nb_coeurs,
                    "score_benchmark": c.score_benchmark,
                }
                for c in _liste_composants(request, Processeur)
            ]
        }
    )


@api
def liste_cartes_graphiques(request):
    """GET /api/cartes-graphiques/?q=rtx : pour l'autocomplétion."""
    return reponse(
        {
            "results": [
                {
                    "modele": c.modele,
                    "fabricant": c.fabricant,
                    "vram_go": c.vram_go,
                    "dediee": c.dediee,
                    "score_benchmark": c.score_benchmark,
                }
                for c in _liste_composants(request, CarteGraphique)
            ]
        }
    )


@api
def filtres_disponibles(request):
    """GET /api/filtres/ : valeurs possibles pour construire les filtres du front."""
    prix = Offre.objects.filter(actif=True, disponibilite__in=DISPONIBLES).aggregate(
        mini=Min("prix"), maxi=Max("prix")
    )
    rams = (
        ProduitPC.objects.exclude(ram_go__isnull=True)
        .values_list("ram_go", flat=True)
        .distinct()
        .order_by("ram_go")
    )
    return reponse(
        {
            "types": [{"code": c, "libelle": l} for c, l in ProduitPC.TypePC.choices],
            "usages": [{"code": c, "libelle": l} for c, l in ProduitPC.Usage.choices],
            "etats": [{"code": c, "libelle": l} for c, l in Offre.Etat.choices],
            "tris": list(TRIS),
            "ram_go": list(rams),
            "prix": {"min": num(prix["mini"]), "max": num(prix["maxi"])},
        }
    )