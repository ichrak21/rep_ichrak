import coreapi
import coreschema
from rest_framework import filters
from django.utils.encoding import force_text
from referentiels.api import models

class CodePostalFilterBackend(filters.BaseFilterBackend):

    def get_schema_fields(self, view):
        """ Ajout d'un paramètre de filtre 
        cf. https://www.django-rest-framework.org/api-guide/filtering/
        """
        return [coreapi.Field(
            name='codePostal',
            location='query',
            required=False,
            schema=coreschema.Integer(
                title='codePostal',
                description=force_text('Permet de recherche la CCI correspond au code postal')
            )
        )]

    def filter_queryset(self, request, queryset, view):
        pass

class CCICodePostalFilterBackend(CodePostalFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
        Filtre la requête si un codePostal est présent dans la querystring
        cci?codePostal=###
        """
        code_postal = request.query_params.get('codePostal', None)
        if code_postal is not None:
            codepostal = models.CodePostal.objects.get(code = code_postal)
            acheminement = models.Acheminement.objects.filter(code_postal = codepostal).first()
            queryset = queryset.filter(communes = acheminement.commune)
        return queryset

class CFECodePostalFilterBackend(CCICodePostalFilterBackend):
    pass

class CommuneCodePostalFilterBackend(CodePostalFilterBackend):

    def filter_queryset(self, request, queryset, view):
        """
        Filtre la requête si un codePostal est présent dans la querystring
        commune?codePostal=###
        """
        code_postal = request.query_params.get('codePostal', None)
        if code_postal is not None:
            acheminements = models.Acheminement.objects.filter(code_postal__code = code_postal)
            communes = [a.commune.code for a in acheminements]
            queryset = queryset.filter(code__in = communes)
        return queryset

class LibelleCommuneFilterBackend(filters.BaseFilterBackend):

    def get_schema_fields(self, view):
        """ Ajout d'un paramètre de filtre 
        cf. https://www.django-rest-framework.org/api-guide/filtering/
        """
        return [coreapi.Field(
            name='libelle',
            location='query',
            required=False,
            schema=coreschema.String(
                title='Libelle',
                description=force_text('Recherche de type contient par libellé de commune')
            )
        )]

    def filter_queryset(self, request, queryset, view):
        """ Applique le filtre par libellé de commune """
        libelle = request.query_params.get('libelle', None)
        if libelle is not None:
            queryset = models.Commune.objects.filter(libelle__icontains=libelle)
        return queryset

   
