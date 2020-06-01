from referentiels import settings
from authlib.integrations.requests_client import OAuth2Session
from django.shortcuts import redirect, HttpResponse
from rest_framework.response import Response
from requests.auth import HTTPBasicAuth

def get_jwt(access_token):
    from authlib.jose import jwt
    public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyi7yZQmSCcMjcLxz+/qZe8eTzqcesfWJ71soc80/Bw0ccd9Oftk6HJsdSa86nXPlcbvS/eM2+u5o0MHZNjk0f04sc8KO+U0HWLTrpVP8mcG5VCL51vGlrIvv6Mvb+id0PZxqVP8e+Pp1z1lL7QJLyjWgx6XMr53S9b8Ek2a/TTqaWQTrx/xm7pLsN8UGOqi37vsHt0MOdWqx9Y7K87PIxDFky7z0dxdB0/pDknt7o38cUnQmh46xcuZbBCNu9RmozZ0s4mSU7a4d8qiM41SY8GQoz3NyUpALgdnqZ6jSgnxvZql1sLmQJhMeLYRkkDDbKNQLdxmG3Q4mGDQ1vE1QlwIDAQAB"
    key = '-----BEGIN PUBLIC KEY-----\n' + public_key + '\n-----END PUBLIC KEY-----'
    key_binary = key.encode('ascii')
    claims = jwt.decode(access_token, key_binary)
    return claims

def check_authorize(session):
    client_id = settings.client_id
    client_secret = settings.client_secret
    redirect_uri = settings.redirect_login
    authorization_endpoint = settings.authorization_endpoint
    settings.LOGGER.debug(authorization_endpoint)
    token_endpoint = settings.token_endpoint
    if 'access_token' not in session:
        return False
    
    
    token = session['access_token']

    # Pass in payload Request JWT Token
    payload: str = f'token_type_hint=requesting_party_token&token={token}'
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
    session = OAuth2Session(client_id, client_secret)
    # With this session, request if Token from request is active
    response = session.request("POST", url,
                                data=payload,
                                headers=headers,
                                auth=HTTPBasicAuth(client_id, client_secret))
    # True/False response from Provider
    auth_provider_response: dict = response.json()

    if auth_provider_response.get('active')!=True:
        return False

    email = get_jwt(token)['email']

    if settings.DEBUG:
        settings.LOGGER.debug(response.json())
        settings.LOGGER.debug(get_jwt(token))

    if 'ccifrance.fr' not in email:
        return False

    return True

def login_authlib(request):
    
    if not request.GET['redirect_uri']:
        return HttpResponse("redirect_uri environment variable is required")

    if not settings.redirect_login:
        return HttpResponse("redirect_login environment variable is required")

    client_id = settings.client_id
    client_secret = settings.client_secret
    redirect_uri = settings.redirect_login + '?redirect_uri=' + request.GET['redirect_uri']
    ## endpoint + response
    authorization_response = request.build_absolute_uri()
    authorization_endpoint = settings.authorization_endpoint
    settings.LOGGER.debug("redirect_uri....................................................")
    settings.LOGGER.debug(settings.redirect_login)
    
    scope = 'openid email profile'
    session = OAuth2Session(client_id, client_secret)
    uri, state = session.create_authorization_url(authorization_endpoint, redirect_uri=redirect_uri, access_type="offline")
    settings.LOGGER.debug(uri)

    return redirect(uri)


def login_callback_authlib(request):

    client_id = settings.client_id
    client_secret = settings.client_secret
    redirect_uri = settings.redirect_login+'?redirect_uri='+request.GET['redirect_uri']
    authorization_response = request.build_absolute_uri()

    authorization_endpoint = settings.authorization_endpoint
    token_endpoint = settings.token_endpoint
    scope = 'openid email profile'
    session = OAuth2Session(client_id, client_secret)
    token = session.fetch_token(token_endpoint, authorization_response=authorization_response, redirect_uri=redirect_uri)

    settings.LOGGER.debug(token['access_token'])
    request.session['access_token'] = token['access_token']

    redirect_sso = request.GET['redirect_uri']

    return redirect(redirect_sso)
