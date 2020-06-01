"""referentiels URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from referentiels.api import views
from referentiels import authlib
from referentiels.signature import views as signature_views
from django.conf.urls.static import static
from django.conf import settings


ROUTER = routers.DefaultRouter()
ROUTER.register(r'cci', views.CCIViewSet)
ROUTER.register(r'cfe', views.CFEViewSet)
ROUTER.register(r'geographique/continents', views.ContinentViewSet)
ROUTER.register(r'geographique/pays', views.PaysViewSet)
ROUTER.register(r'geographique/regions', views.RegionViewSet)
ROUTER.register(r'geographique/departements', views.DepartementViewSet)
ROUTER.register(r'geographique/communes', views.CommuneViewSet)
ROUTER.register(r'geographique/codespostaux', views.CodePostalViewSet)
ROUTER.register(r'geographique/acheminements', views.AcheminementViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    url('referentiels/v2/', include(ROUTER.urls)),
    url(r'^docs/', include_docs_urls(title='API référentiel V2', public=False)),
    path('line[26]/', views.hello_world),
    url(r'^cci_list/$', views.simple_view),
    url(r'^personnel$', views.import_personnel, name='personnel'), 
    path('hello_world/', views.hello_world),
    path('personnel/edit/<pk>/', views.edit, name='edit'),
    path('personnel/post/', views.postview, name='addPerso'),
    path('personnel/delete/<id_perso>/', views.delete, name='delete'),
    path('prt/', views.validate_token),

    url(r'^cci_list/$', views.simple_view),
    url(r'^login/$', views.login),  # append demo view
    url(r'^login_authlib/$', authlib.login_authlib),  # append demo view
    url(r'^login/callback_authlib/$', authlib.login_callback_authlib),  # just http response user information

    # api personnel
    url(r'^personnel$', views.import_personnel, name='personnel'),
    url(r'^get_personnel$', views.get_personnel, name='get_personnel'),
    url(r'^personnel_information_2019$', views.personnel_information_2019, name='personnel_information_2019'),
    url(r'^personnel_information$', views.personnel_information, name='personnel_information'),
    url(r'^search$', views.search, name='search'),
    url(r'^import_contact_sendinblue$', views.import_contact_sendinblue),
    url(r'^create_attributes/(\w+)$', views.create_attributes),

    # api signature
    path('signature/get_documents_recipient', signature_views.get_documents_recipient),
    path('signature/get_documents_sender', signature_views.get_documents_sender),
    url(r'^signature/add_signature/(\d+)$', signature_views.post_signature),
    url(r'^signature/get_one_document/(\d+)$', signature_views.get_one_document),
    url(r'^signature/search$', signature_views.search),
    url(r'^signature/add_document$', signature_views.post_document),
    url(r'^signature/send_email$', signature_views.send_messages),
    url(r'^signature/get_all_documents$', signature_views.get_all_documents),
    url(r'^signature/add_note_frais$', signature_views.post_note_frais)
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



