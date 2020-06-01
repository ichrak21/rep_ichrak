import os
import csv
from pprint import pprint
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, pagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from referentiels import authlib

from authlib.integrations.requests_client import OAuth2Session
from requests.auth import HTTPBasicAuth
from django.shortcuts import redirect, HttpResponse, get_object_or_404
from django.conf import settings
from reversion.models import Version
from django.shortcuts import render
import pandas as pd
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity
from functools import reduce
import operator
import requests

from .forms import PostForm
from .models import Personnel
from django.core import serializers
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Count
import json

from referentiels.api.models import Personnel, CCI, CFE, Continent, Pays, Region, \
    Departement, Commune, CodePostal, Acheminement, Adresse

from referentiels.api.serializers import CCISerializer, CFESerializer, \
    ContinentSerializer, PaysSerializer, RegionSerializer, \
    DepartementSerializer, CommuneSerializer, CodePostalSerializer, \
    AcheminementSerializer, AdresseSerializer
from referentiels.api import filters_backend

from referentiels import settings

from django.shortcuts import render
from jinja2 import Environment, FileSystemLoader
from rest_framework.permissions import IsAuthenticated

TEMPLATE_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/api/templates/'
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)


class IpPermission(BasePermission):
    """
    Allow white list ip to access to resource
    """

    # cf. referentiels/settings.py
    # WHITE_LIST_IP = ['81.255.90.115', '127.0.0.1', 'localhost']

    def has_permission(self, request, view):
        """
        Check remote if remote IP address is in WHITE_LIST_IP
        :param request:
        :param view:
        :return:
        """
        # Get request remote IP
        remote_ip = request.META.get('REMOTE_ADDR')
        # Check
        if remote_ip in settings.WHITE_LIST_IP:
            return True
        else:
            return False


class CciPermission(BasePermission):
    """
    Use this permission with decorator or class

    Usage in view function

    from rest_framework.decorators import api_view, permission_classes
    from rest_framework.response import Response

    @api_view(['GET', 'POST'])
    @permission_classes((CciPermission,))
    def api_test(request):
        return Response({'credentials_valid': True})

    ---------------------------

    Usage in class
    from rest_framework.views import APIView
    from rest_framework.response import Response

    class ExampleView(APIView):
    permission_classes = (CciPermission,)

    def get(self, request, format=None):
        content = {
            'status': 'request was permitted'
        }
        return Response(content)

    """

    @staticmethod
    def get_jwt(_client_id: str = 'referential',
                _client_secret: str = '70bb87bc-bc95-46e2-8914-396c38af51b4',
                _token_endpoint: str = 'https://sso.cciconnect.fr/realms/connect/protocol/openid-connect/token'):
        """
            Get Bearer token with client ID, client SECRET and token Endpoint
            :param _client_id:
            :param _client_secret:
            :param _token_endpoint:
            :return:
            """
        session = ol2(_client_id, _client_secret)
        response: dict = session.fetch_token(_token_endpoint, grant_type='client_credentials')
        return response

    def has_permission(self, request, view):
        """
        Main method: will JWT to Auth Provider
        return true/false for resource permission
        :param request:
        :param view:
        :return:
        """

        # Don't give access if not:
        #   - HTTP_AUTHORIZATION is not header
        #   - client_id is not in body
        #   - client_secure is not in body
        if not request.META.get('HTTP_AUTHORIZATION') \
                or not request.data.get('client_id') \
                or not request.data.get('client_secret'):
            return False

        # Proceed to verification to Auth Provider
        # if JWT still active
        else:
            # Get credentials parameters to check
            _request_token: str = request.META.get('HTTP_AUTHORIZATION').replace('Bearer ', '')
            _client_id: str = request.data.get('client_id')
            _client_secret: str = request.data.get('client_secret')

            # Pass in payload Request JWT Token
            payload: str = f'token_type_hint=requesting_party_token&token={_request_token}'
            # Construct header
            headers: dict = {'Content-Type': "application/x-www-form-urlencoded",
                             'Host': "sso.cciconnect.fr",
                             'accept-encoding': "gzip, deflate",
                             'content-length': "102",
                             'Connection': "keep-alive",
                             'cache-control': "no-cache"
                             }
            # Define token introspection url
            url: str = 'https://sso.cciconnect.fr/realms/connect/protocol/openid-connect/token/introspect'
            # Create a new session with client id and client secret to consult auth provider
            session = OAuth2Session(_client_id,
                                    token=self.get_jwt(_client_id=_client_id, _client_secret=_client_secret))
            # With this session, request if Token from request is active
            response = session.request("POST", url,
                                       data=payload,
                                       headers=headers,
                                       auth=HTTPBasicAuth(_client_id, _client_secret))
            # True/False response from Provider
            auth_provider_response: dict = response.json()
            return auth_provider_response.get('active')


class ReferentielPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000


class CCIViewSet(viewsets.ModelViewSet):
    """
    list:
    Liste des CCI. Le paramètre **codePostal** permet d'effectuer une recherche de CCI par code postal.
    **cci?codePostal=###**

    create:
    Création d'une nouvelle CCI

    """
    permission_classes = (IpPermission, CciPermission)
    queryset = CCI.objects.all()
    serializer_class = CCISerializer
    pagination_class = ReferentielPagination
    filter_backends = (filters_backend.CCICodePostalFilterBackend,)

    def retrieve(self, request, pk=None):
        """ Retourne les informations d'une CCI pour le **code** donné
        cci/{code}
        """
        cci = get_object_or_404(self.queryset, code=pk)
        serializer = CCISerializer(cci)
        return Response(serializer.data)

    @action(detail=True)
    def cfe(self, request, pk=None):
        """ Retourne la liste des CFE pour une CCI
        cci/{code}/cfe
        """
        cci = get_object_or_404(self.queryset, code=pk)
        cfes = CFE.objects.filter(cci=cci)
        s = [CFESerializer(v).data for v in cfes]
        return Response(s)


class CFEViewSet(viewsets.ModelViewSet):
    """
    list:
    Liste des CFE

    create:
    Création d'un nouveau CFE

    """
    permission_classes = (IpPermission, CciPermission)
    queryset = CFE.objects.all()
    serializer_class = CFESerializer
    pagination_class = ReferentielPagination
    filter_backends = (filters_backend.CFECodePostalFilterBackend,)

    def retrieve(self, request, pk=None):
        """ Retourne les informations d'une CCI pour le **code** donné
        cfe/{code}
        """
        cfe = get_object_or_404(self.queryset, code=pk)
        serializer = CFESerializer(cfe)
        return Response(serializer.data)


class AdresseViewSet(viewsets.ModelViewSet):
    """
    list:
    Liste des adresses
    
    create:
    Création d'une nouvelle adresse"
    """
    permission_classes = (IpPermission, CciPermission)
    queryset = Adresse.objects.all()
    serializer_class = AdresseSerializer
    pagination_class = ReferentielPagination


class ContinentViewSet(viewsets.ModelViewSet):
    """
    list:
    Liste des continents
    
    create:
    Création d'un nouveau continent
    """
    permission_classes = (IpPermission, CciPermission)
    queryset = Continent.objects.all()
    serializer_class = ContinentSerializer
    pagination_class = ReferentielPagination


class PaysViewSet(viewsets.ModelViewSet):
    """
    list:
    Liste des pays
    
    create:
    Création d'un nouveau pays
    """
    permission_classes = (IpPermission, CciPermission)
    queryset = Pays.objects.all()
    serializer_class = PaysSerializer
    pagination_class = ReferentielPagination

    @action(detail=True)
    def history(self, request, pk=None):
        """ Permet d'afficher l'historique via l'appel du service 
        pays/{pk}/history
        """
        versions = Version.objects.get_for_object_reference(Pays, pk)
        serializer = [PaysSerializer(v.field_dict).data for v in versions]
        return Response(serializer)


class PaysHistoryViewSet(viewsets.ViewSet):
    """
    list:
    Liste des pays
    
    create:
    Création d'un nouveau pays
    """
    serializer_class = PaysSerializer
    queryset = Pays.objects.all()
    pagination_class = ReferentielPagination

    def retrieve(self, request, pk=None, revision=None):
        settings.LOGGER.debug(pk)
        settings.LOGGER.debug(revision)
        queryset = Pays.objects.all()
        pays = get_object_or_404(queryset, pk=pk)
        versions = Version.objects.get_for_object(pays)
        serializer = PaysSerializer(versions[revision])
        return Response(serializer.data)


class RegionViewSet(viewsets.ModelViewSet):
    """
    list:
    Liste des régions
    
    create:
    Création d'une nouvelle région
    """
    permission_classes = (IpPermission, CciPermission)
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class DepartementViewSet(viewsets.ModelViewSet):
    """
    list:
    Liste des départements
    
    create:
    Création d'un nouveau département
    """
    permission_classes = (IpPermission, CciPermission)
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer
    pagination_class = ReferentielPagination

    def retrieve(self, request, pk=None):
        """ Retourne les informations d'un département pour le **code** donné
        departements/{code}
        """
        departement = get_object_or_404(self.queryset, code=pk)
        serializer = DepartementSerializer(departement)
        return Response(serializer.data)

    @action(detail=True)
    def communes(self, request, pk):
        """ Retourne la liste des communes d'un département
        """
        departement = get_object_or_404(self.queryset, code=pk)
        communes = Commune.objects.filter(departement=departement)
        serializer = [CommuneSerializer(v).data for v in communes]
        return Response(serializer)


class CommuneViewSet(viewsets.ModelViewSet):
    """
    list:
    Liste des communes
    
    create:
    Création d'une nouvelle commune
    """
    permission_classes = (IpPermission, CciPermission)
    queryset = Commune.objects.all()
    serializer_class = CommuneSerializer
    pagination_class = ReferentielPagination
    filter_backends = (
        filters_backend.CommuneCodePostalFilterBackend,
        filters_backend.LibelleCommuneFilterBackend,
    )

    def retrieve(self, request, pk=None):
        """ Retourne les informations d'une commune pour le **code** donné
        commune/{code}
        """
        commune = get_object_or_404(self.queryset, code=pk)
        serializer = CommuneSerializer(commune)
        return Response(serializer.data)
    # TODO : Shan->Olivier j'ai mergé dev_cicd -> master
    # TODO : est-ce que tu peux checker cette méthode ?
    # TODO : elle n'existe plus dans ma branche
    def get_queryset(self):
        """
        Filtre la requête si un codePostal est présent dans la querystring
        cci?codePostal=### ou si un libelle est présent cci?libelle=###
        """
        queryset = Commune.objects.all()
        code_postal = self.request.query_params.get('codePostal', None)
        libelle = self.request.query_params.get('libelle', None)
        if libelle is not None:
            queryset = Commune.objects.filter(libelle__icontains=libelle)
        elif code_postal is not None:
            acheminements = Acheminement.objects.filter(code_postal__code = code_postal)
            communes = [a.commune.code for a in acheminements]
            queryset = queryset.filter(code__in = communes)
        return queryset


class AcheminementViewSet(viewsets.ModelViewSet):
    """
    list:
    Liste des acheminements
    """
    permission_classes = (IpPermission, CciPermission)
    queryset = Acheminement.objects.all()
    serializer_class = AcheminementSerializer
    pagination_class = ReferentielPagination


class CodePostalViewSet(viewsets.ModelViewSet):
    """
    list:
    Liste des codes postaux
    
    create:
    Création d'un nouveau code postal
    """
    permission_classes = (IpPermission, CciPermission)
    queryset = CodePostal.objects.all()
    serializer_class = CodePostalSerializer
    pagination_class = ReferentielPagination


# @api_view(['GET'])
# TODO : deactivate in prod
def validate_token(request):
    def get_jwt(
            _client_id: str = 'referential',
            _client_secret: str = '70bb87bc-bc95-46e2-8914-396c38af51b4',
            _token_endpoint: str = 'https://sso.cciconnect.fr/realms/connect/protocol/openid-connect/token'
    ):
        """
        Get Bearer token with client ID, client SECRET and token Endpoint
        :param _client_id:
        :param _client_secret:
        :param _token_endpoint:
        :return:
        """
        session = ol2(_client_id, _client_secret)
        response: dict = session.fetch_token(_token_endpoint, grant_type='client_credentials')
        return response

    client_id: str = 'referential'
    client_secret: str = '70bb87bc-bc95-46e2-8914-396c38af51b4'

    # Get only token from request
    if not request.META.get('HTTP_AUTHORIZATION'):
        return Response({'error': 'missing HTTP_AUTHORIZATION'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    req_token = request.META.get('HTTP_AUTHORIZATION').replace('Bearer ', '')
    token = get_jwt()
    session = OAuth2Session(client_id, token=token)
    payload = f'token_type_hint=requesting_party_token&token={req_token}'
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Host': "sso.cciconnect.fr",
        'accept-encoding': "gzip, deflate",
        'content-length': "102",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    url = 'https://sso.cciconnect.fr/realms/connect/protocol/openid-connect/token/introspect'
    r = session.request("POST", url,
                        data=payload,
                        headers=headers,
                        auth=HTTPBasicAuth(client_id, client_secret))

    return Response({'server response': r.json()}, status=status.HTTP_200_OK)


# @api_view(['GET', 'POST'])
# @permission_classes((CciPermission,))
# TODO : deactivated in prod
def api_test_cred(request):
    """
    Example usage of CciPermission with functions based resource
    :param request:
    :return:
    """
    return Response({'credentials_valid': True})


# TODO : deactivated in prod
class ApiTestCred(object):  # APIView):
    """
    Example usage of CciPermission with class based resource
    """

    # Override default ApiView permission
    # Default = api_settings.DEFAULT_PERMISSION_CLASSES
    permission_classes = (CciPermission,)

    def get(self, request, format=None):
        return Response({'credentials_valid': True})

    def post(self, request, format=None):
        return Response({'credentials_valid': True})


# @api_view(['GET', 'POST'])
# @permission_classes((IpPermission,))
# TODO : deactivated in prod
def ip_restriction_test(request):
    """
    Example of usage for IP restriction
    :param request:
    :return:
    """
    return Response({'ip allowed': True})


# @api_view(['GET', 'POST'])
# TODO : deactivated in prod
def return_ip(request):
    pprint(request.META)

    return Response({
        'client ip': request.META.get('REMOTE_ADDR')
    })


@api_view(['GET', 'POST'])
def hello_world(request):
    return Response(request.COOKIES)
    return Response({'server_response': 'HELLO WORLD DEPLOY 4'})


@api_view(['GET', 'POST'])
def simple_view(request):
    if not check_authorize(request.session):
        return redirect('/login_authlib')

    search_bar = request.GET.get('search')

    # Fetch from db
    # cci id, name, phone, remove duplicate, filter only active CCI

    cci_list = CCI.objects.values('id_cci', 'nom', 'telephone').filter(actif=True).distinct()

    _vars = {
        'cci_list': cci_list
    }

    return render(request, TEMPLATE_PATH + 'simple_view.html', _vars)

def login(request):

    """ Initiate authentication """
    auth_url, state = settings.KEYCLOAK_CLIENT.authentication_url()
    request.session['state'] = state
    
    return redirect(auth_url)


def login_callback(request):
    """ Authentication callback handler """

    code = request.GET.get('code')
    state = request.GET.get('state', 'unknown')
    # validate state
    _state = request.session.pop('state', None)
    if state != _state:
        return HttpResponse('Invalid state', status=403)

    # retrieve user info
    response = settings.KEYCLOAK_CLIENT.authentication_callback(code)
    user_info = settings.KEYCLOAK_CLIENT.decode_jwt(response['id_token'])

    settings.LOGGER.debug(" CALLBACK URL -----------------------------------")
    settings.LOGGER.debug(response)
    settings.LOGGER.debug(user_info)
    settings.LOGGER.debug("-----------------------------------")

    return HttpResponse(user_info)


@api_view(['GET'])
def import_personnel(request):
    if not authlib.check_authorize(request.session):
        return Response({'server response': "authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(PROJECT_ROOT)
    data = open(BASE_DIR+'/test',  encoding ='ISO-8859-1')
    data.readline()
    cpt_success = 0
    cpt_failure = 0
    for line in data:
        line =  line.split(';')
        if (len(line[10])>14 or len(line[11])>14 or len(line[24])>14):
            cpt_failure=cpt_failure+1
            continue

        if line[43] == 'matricule':
            continue
        
        if Personnel.objects.filter(matricule=line[43]):
            tmp = Personnel.objects.get(matricule=line[43])
        else:
            tmp = Personnel()
            tmp.matricule = line[43]
        # return Response({'server_response': line})
        
        tmp.civilite = line[0]
        tmp.prenom = line[1]
        tmp.nom = line[2]
        tmp.direction = line[3]
        tmp.fonction_generique = line[4]
        tmp.fonction_exacte = line[5]
        tmp.date_debut_fonction = line[6]
        tmp.date_fin_fonction = line[7]
        tmp.titre_politesse = line[8]
        tmp.email = line[9]
        tmp.tel_fixe = line[10]
        tmp.tel_mobile = line[11]
        tmp.service = line[12]
        tmp.expertise = line[13]
        tmp.domaine_metier = line[14]
        tmp.centres = line[15]
        tmp.raison_sociale = line[16]
        tmp.n_siret = line[17]
        tmp.adress = line[18]
        tmp.complement_adresse = line[19]
        tmp.BP = line[20]
        tmp.CP = line[21]
        tmp.ville = line[22]
        tmp.pays = line[23]
        tmp.phone = line[24]
        tmp.fax = line[25]
        tmp.site=line[26]
        tmp.type_organisme = line[28]
        tmp.enseigne = line[29]
        tmp.sous_type = line[30]
        tmp.secteur_activite = line[31]
        tmp.code_APE = line[32]
        tmp.effectif = line[33]
        tmp.nombre_ressortissants = line[34]
        tmp.id_annuaire = line[35]
        tmp.source_import = line[36]
        tmp.region = line[37]
        tmp.departement=line[38]
        tmp.linkedin=line[39]
        tmp.facebook=line[40]
        tmp.tweeter=line[41]
        tmp.radiation=line[42]
        tmp.save()
        cpt_success=cpt_success+1

    data.close()
    #print(request)
    return HttpResponse(cpt_success)

@api_view(['GET'])
def get_personnel(request):
    if not authlib.check_authorize(request.session):
        settings.LOGGER.debug('DEBUG authorize session!')
        return Response({'server response': "authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    perso_list = list(Personnel.objects.values("id","matricule", "phone", "civilite", "nom", "prenom", "email", "direction", "fonction_exacte", "raison_sociale").order_by('matricule').distinct('matricule')[:300])
    cookies = request.COOKIES
    settings.LOGGER.debug(cookies)
    _vars = {
        'perso_list': perso_list,
        'cookies': cookies
    }
    return Response(perso_list)


def postview(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('personnel')
        
    form = PostForm()

    return render(request,'add_perso.html',{'form': form})

def edit(request, pk, template_name='edit_perso.html'):
    post= get_object_or_404(Personnel, pk=int(pk))
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('personnel')
    return render(request, template_name, {'form':form})

def delete(request, id_perso):
    perso = Personnel.objects.get(id=id_perso)
    perso.delete()
    return redirect('personnel')

@api_view(['GET', 'POST'])
def search(request):
    if not authlib.check_authorize(request.session):
        return HttpResponse({'server response': "authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method != 'GET':
        return HttpResponse('NOT GET')

    src = request.GET['perso']

    # If no query from user
    if not src:
        return HttpResponse('NOT SRC')

    query_list = src.split()
    queryset = Personnel.objects.values("matricule","nom", "prenom", "email", "raison_sociale", 'fonction_exacte').filter(
            reduce(operator.and_, (Q(prenom__istartswith=q)|Q(nom__istartswith=q)|Q(email__icontains=q)|Q(raison_sociale__icontains=q)|Q(fonction_exacte__icontains=q)|Q(matricule__icontains=q) for q in query_list)) 
        )
    return Response(list(queryset))

    if match:
        return HttpResponse(queryset, content_type='application/json')

    return HttpResponse('NOT MATCH')

@api_view(['GET', 'POST'])
def personnel_information_2019(request):

    datee_2019=Personnel.objects.filter(date_debut_fonction__icontains='2019').all().count()
    collaborateur_CCI= Personnel.objects.all().values('ville').annotate(total=Count('ville')).order_by('total')
    collab_cci_par_cci = Personnel.objects.filter(date_debut_fonction__icontains='2019').all().values('raison_sociale').annotate(total=Count('raison_sociale')).order_by('total')
    #collab_cci_par_date= Personnel.objects.exclude(date_debut_fonction__icontains='2019').all()
    collab_cci_par_direction= Personnel.objects.filter(date_debut_fonction__icontains='2019').all().values('direction').annotate(total=Count('direction')).order_by('total')   
    nb_collaborateur_homme = Personnel.objects.filter(date_debut_fonction__icontains='2019').all().filter(civilite__icontains='Monsieur').all().count()
    nb_collaborateur_femme = Personnel.objects.filter(date_debut_fonction__icontains='2019').all().filter(civilite__icontains='Madame').all().count()
    return Response({ 'nb_collaborateur_homme': nb_collaborateur_homme ,'nb_collaborateur_femmme': nb_collaborateur_femme, 'nb_collaborateur_2019': datee_2019,  "CCI" : collab_cci_par_cci })

@api_view(['GET', 'POST'])
def personnel_information(request):
    collab_cci_par_date= Personnel.objects.exclude(date_debut_fonction__icontains='2019').all().count()
    collaborateur_CCI= Personnel.objects.all().values('ville').annotate(total=Count('ville')).order_by('total')
    collab_cci_par_cci = Personnel.objects.all().values('raison_sociale').annotate(total=Count('raison_sociale')).order_by('total')
    collab_cci_par_direction= Personnel.objects.all().values('direction').annotate(total=Count('direction')).order_by('total')
    nb_collaborateur_homme = Personnel.objects.filter(civilite__icontains='Monsieur').all().count()
    nb_collaborateur_femme = Personnel.objects.filter(civilite__icontains='Madame').all().count()
    nb_collaborateur_homme_cci=Personnel.objects.filter(civilite__icontains='Monsieur').all().values('raison_sociale').annotate(total=Count('raison_sociale')).order_by('total')
    nb_collaborateur_femme_cci=Personnel.objects.filter(civilite__icontains='Madame').all().values('raison_sociale').annotate(total=Count('raison_sociale')).order_by('total')
    return Response({'nb_collaborateurs' : collab_cci_par_date ,  'nb_collaborateur_homme': nb_collaborateur_homme ,'nb_collaborateur_femmme': nb_collaborateur_femme ,"CCI" : collab_cci_par_cci, 'nb_collaborateur_homme_cci': nb_collaborateur_homme_cci, 'nb_collaborateur_femme_cci': nb_collaborateur_femme_cci})

@api_view(['GET', 'POST'])
def import_contact_sendinblue(request):
    if not authlib.check_authorize(request.session):
        return HttpResponse({'server response': "authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    url = settings.URL_SENDINBLUE
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'api-key': settings.API_KEY_SENDINBLUE
        }
    personnel= list(Personnel.objects.values("nom", "prenom", "email", "phone", "raison_sociale").order_by('email').distinct('email'))

    for i in range(len(personnel)):
        settings.LOGGER.debug(i)
        # Get user by email
        response_user = requests.request("GET", url + '/' + personnel[i]['email'], headers=headers)

        # If the request for get the email is success : user already exist
        if response_user.status_code == 200:
            settings.LOGGER.debug('update')
            payload={
                "attributes": {
                    "lastname": personnel[i]['nom'],
                    "firstname": personnel[i]['prenom'],
                    "phone": personnel[i]['phone'].replace(" ",""),
                    "social_reason": personnel[i]['raison_sociale']
                }
            }
            settings.LOGGER.debug(personnel[i]['email'])
            settings.LOGGER.debug(url+'/'+personnel[i]['email'])
            settings.LOGGER.debug(json.dumps(payload))
            response = requests.request("PUT", url + '/' + personnel[i]['email'], data=json.dumps(payload), headers=headers)
            if response.status_code != 204:
                settings.LOGGER.debug(response.text)
            continue

        # User not exist : send create
        payload ={
            "email": personnel[i]['email'],
            "attributes": {
                "lastname": personnel[i]['nom'],
                "firstname": personnel[i]['prenom'],
                "phone": personnel[i]['phone'].replace(" ",""),
                "social_reason": personnel[i]['raison_sociale']
            }
        }
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        if response.status_code != 201:
                settings.LOGGER.debug(response.text)

    return Response(response)

@api_view(['GET', 'POST'])
def create_attributes(request, attribute):
    if not authlib.check_authorize(request.session):
        return HttpResponse({'server response': "authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
    url = settings.URL_SENDINBLUE

    payload = {
        "type": "text"
    }
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'api-key': settings.API_KEY_SENDINBLUE
    }
    # Create attributes for sendinblue : add name of attribute in url exp: create_attributes/name_attributes
    response = requests.request("POST", url + '/attributes/normal/'+attribute , data=json.dumps(payload), headers=headers)
    if response.status_code != 201:
                settings.LOGGER.debug(response.text)
                
    return Response(response)