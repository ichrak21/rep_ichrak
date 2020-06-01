# coding=utf-8
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from requests_oauthlib import OAuth2Session
from authlib.client import OAuth2Session as ol2
from requests.auth import HTTPBasicAuth
from referentiels.api import models
from referentiels.api import views

# from rest_framework.test import APIRequestFactory
# factory = APIRequestFactory()
# request = factory.post('/ref/cci/', {'nom': 'TestCase', 'actif': True, 'code': 999, 'type': 'CCI'})

## Django status codes 
#  https://www.django-rest-framework.org/api-guide/status-codes/

PREFIXE = '/referentiels/v2'


class TestOAuth(TestCase):
    def setUp(self) -> None:
        self.client_id: str = 'referential'
        self.client_secure: str = '70bb87bc-bc95-46e2-8914-396c38af51b4'
        self.token_endpoint: str = 'https://sso.cciconnect.fr/realms/connect/protocol/openid-connect/token'

    @staticmethod
    def get_jwt(_client_id: str, _client_secret: str, _token_endpoint: str):
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

    def test_token_validation(self):
        test_token = self.get_jwt(self.client_id, self.client_secure, self.token_endpoint).get('access_token')
        # Pass in payload Request JWT Token
        payload: str = f'token_type_hint=requesting_party_token&token={test_token}'
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
        session = OAuth2Session(self.client_id,
                                token=self.get_jwt(_client_id=self.client_id,
                                                   _client_secret=self.client_secure,
                                                   _token_endpoint=self.token_endpoint))
        # With this session, request if Token from request is active
        r = session.request("POST", url,
                            data=payload,
                            headers=headers,
                            auth=HTTPBasicAuth(self.client_id, self.client_secure))
        # True/False response from Provider
        auth_provider_response: dict = r.json()
        self.assertTrue(auth_provider_response.get('active'))

# Create your tests here.
class RegionTests(APITestCase):
    def setUp(self):
        self.data = {'code': '1', 'code_consulaire': '1', 'libelle': 'Bretagne'}
        self.url = PREFIXE + '/geographique/regions/'

    def test_post_region(self):
        """ Test création d'une région"""
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Region.objects.count(), 1)
        self.assertEqual(models.Region.objects.get().libelle, 'Bretagne')

    def test_get_region(self):
        """ Test affichage du service """
        self.test_post_region()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['libelle'], 'Bretagne')


class CCITests(APITestCase):

    def setUp(self):
        self.data = {'nom': 'TestCase', 'actif': True, 'code': 999, 'type': 'CCI'}
        self.url = PREFIXE + '/cci/'
        # Désactive le contrôle vers CCiconnect pour les tests
        views.CciPermission.has_permission = lambda x, y, z: True

    def test_post_cci(self):
        """ Test création d'une entrée CCI """
        response = self.client.post(self.url, self.data, format='json')
        # https://www.django-rest-framework.org/api-guide/status-codes/
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.CCI.objects.count(), 1)
        self.assertEqual(models.CCI.objects.get().nom, 'TestCase')

    def test_get_cci(self):
        """ Test affichage du service """
        self.test_post_cci()
        #cci_id = str(models.CCI.objects.get().id)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['nom'], 'TestCase')

    def _test_search_cci_par_codepostal_inexistant(self):
        """ Test l'exception CodePostal.DoesNotExist """
        self.test_post_cci()
        url = self.url + '?codePostal=99900'
        self.assertRaises(models.CodePostal.DoesNotExist, self.client.get, url, format='json')

    def test_search_cci(self):
        """ Test par code postal """
        # Ajout des données code postal
        url_codepostal = PREFIXE + '/geographique/codespostaux/'
        self.client.post(url_codepostal, {'code': '56000'}, format='json')
        code_postal_id = models.CodePostal.objects.get().id

        # Ajout des données CCI
        self.test_post_cci()
        cci_id = str(models.CCI.objects.get().id)

        # Ajout des données commune
        url_communes = PREFIXE + '/geographique/communes/'
        self.client.post(url_communes,
                         {'actif': True, 'article': '', 'code': '56260',
                          'libelle': 'VANNES', 'cci': cci_id},
                         format='json')
        commune_id = models.Commune.objects.get().id

        # Ajout des données acheminement 
        url_acheminements = PREFIXE + '/geographique/acheminements/'
        self.client.post(url_acheminements,
                         {'libelle': 'Vannes', 'code_postal': code_postal_id, 'commune': commune_id}, format='json')
        #acheminement_id = models.Acheminement.objects.get().id

        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['code'], 999)


class CFETest(APITestCase):
    def setUp(self):
        self.data = {'libelle': 'TestCFE', 'actif': False, 'type_cfe': 'C', 'code': 'C9999'}
        self.url = PREFIXE + '/cfe/'

    def test_post_cfe(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.CFE.objects.count(), 1)
        self.assertEqual(models.CFE.objects.get().libelle, 'TestCFE')

    def test_post_cfe_validate_code_error1(self):
        """ Test validate with bad code """
        data = self.data
        data['code'] = 'D9999'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'][0], 'This field should start with a valid type_cfe')

    def test_post_cfe_validate_type_consistency(self):
        data = self.data
        data['code'] = 'G9999'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'][0], 'This field should start with type_cfe')


class CodePostalTests(APITestCase):
    def setUp(self):
        self.data = {'code': '56000'}
        self.url = PREFIXE + '/geographique/codespostaux/'
        self.url_acheminements = PREFIXE + '/geographique/acheminements/'

    def test_post_codepostal(self):
        """ Test création d'un code postal """
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.CodePostal.objects.count(), 1)
        self.assertEqual(models.CodePostal.objects.get().code, '56000')

    def test_get_codepostal(self):
        """ Test affichage du service codespostaux """
        self.test_post_codepostal()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['code'], '56000')

    def test_get_acheminements(self):
        self.test_post_codepostal()
        code_postal_id = models.CodePostal.objects.get().id
        response = self.client.post(self.url_acheminements,
                                    {'libelle': 'Vannes', 'code_postal': code_postal_id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Acheminement.objects.count(), 1)
        self.assertEqual(models.Acheminement.objects.get().libelle, 'Vannes')


class VersionTests(APITestCase):
    def setUp(self):
        self.data = {
            "continent": "UE",
            "actif": True,
            "ancien_nom": "",
            "annee_inde": None,
            "code_actualite": 1,
            "code_ancien_pays": "",
            "codecfe": "50",
            "codeiso2": "FR",
            "codeiso3": "FRA",
            "code_num3": 250,
            "code_officiel_geo": "XXXXX",
            "code_pays_ratt": "",
            "esteee": False,
            "estue": True,
            "libelle": "FRANCE",
            "libelle_complet": "RÉPUBLIQUE FRANÇAISE",
            "nationalite": "Français"
        }
        self.url = PREFIXE + '/geographique/pays/'

    def test_post_pays(self):
        """ Création d'un pays via l'API """
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Pays.objects.count(), 1)
        self.assertEqual(models.Pays.objects.get().libelle, 'FRANCE')

    def test_put_pays(self):
        """ Test mise à jour d'un pays """
        self.test_post_pays()
        update = {
            "libelle": "TEST",
            "code_num3": 250,
            "esteee": False,
            "estue": True,
        }
        response = self.client.put(self.url + "1/", data=update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["libelle"], "TEST")
        response = self.client.get(self.url + "1/", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["libelle"], "TEST")
    
    def test_put_pays_history(self):
        """ Pas d'historisation lors de la mise à jour VIA l'API """
        self.test_post_pays()
        update = {
            "libelle": "TEST SUITE",
            "code_num3": 250,
            "esteee": False,
            "estue": True,
        }
        response = self.client.put(self.url + "1/", data=update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url + "1/history/", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


# class FakeError(TestCase):
#
#     def setUp(self) -> None:
#         pass
#
#     def test_do_error(self):
#         self.assertTrue(False)
