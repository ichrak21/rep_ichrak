from django.shortcuts import render
from .models import Signature
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from referentiels import authlib
from rest_framework import status
from functools import reduce
from django.shortcuts import redirect, HttpResponse, get_object_or_404
from django.db.models import Q
from rest_framework.parsers import FileUploadParser
from django.core.mail.backends.smtp import EmailBackend
from .serializers import FileSerializer
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
import smtplib
import operator


@api_view(['GET'])
def get_documents_recipient(request):
    if not authlib.check_authorize(request.session):
        return Response({'server response': "authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    email = authlib.get_jwt(request.session['access_token'])['email']
    settings.LOGGER.debug(email)
    list_document = list(Signature.objects.values("id", "name", "description", "document", "signature_image", "sender_email", "recipient_email", "creation_date", "date_signature").filter(Q(recipient_email = email)))
    
    return Response(list_document)

@api_view(['GET'])
def get_documents_sender(request):
    if not authlib.check_authorize(request.session):
        return Response({'server response': "authentication required"}, status = status.HTTP_401_UNAUTHORIZED)

    email = authlib.get_jwt(request.session['access_token'])['email'] 
    list_document = list(Signature.objects.values("id", "name", "description", "document", "signature_image", "sender_email", "recipient_email", "creation_date", "date_signature").filter(Q(sender_email = email)))
    
    return Response(list_document)

@api_view(['GET'])
def get_all_documents(request):
    if not authlib.check_authorize(request.session):
        return Response({'server response': "authentication required"}, status = status.HTTP_401_UNAUTHORIZED)

    email = authlib.get_jwt(request.session['access_token'])['email'] 
    list_document = list(Signature.objects.values("id", "name", "description", "document", "signature_image", "sender_email", "recipient_email", "creation_date", "date_signature").filter(Q(sender_email = email) | Q(recipient_email = email) ))
    
    return Response(list_document)

@api_view(['POST'])
def post_signature(request, id_doc):
    if not authlib.check_authorize(request.session):
        return Response({'server response': "authentication required"}, status = status.HTTP_401_UNAUTHORIZED)

    if not request.method == 'POST':
        return Response(False)

    signature = Signature.objects.get(id = id_doc)
    signature.signature_image = request.POST['data']
    signature.date_signature = request.POST['date']
    settings.LOGGER.debug(request.POST['date'])
    settings.LOGGER.debug(request.POST['data'])
    signature.save()
    return Response(True)

@api_view(['GET'])
def get_one_document(request, id_doc):
    if not authlib.check_authorize(request.session):
        return Response({'server response': "authentication required"}, status = status.HTTP_401_UNAUTHORIZED)
        
    document = Signature.objects.values("id", "name", "description", "document", "signature_image", "sender_email", "recipient_email", "creation_date", "date_signature").get(id = id_doc)
    settings.LOGGER.debug(document)

    return Response(document)
@api_view(['GET', 'POST'])
def search(request):
    if not authlib.check_authorize(request.session):
        return HttpResponse({'server response': "authentication required"}, status = status.HTTP_401_UNAUTHORIZED)

    if request.method != 'GET':
        return HttpResponse('NOT GET')

    src = request.GET['doc']

    # If no query from user
    if not src:
        return HttpResponse('NOT SRC')
        
    email = authlib.get_jwt(request.session['access_token'])['email']
    query_list = src.split()
    queryset = Signature.objects.values("id", "name", "description", "document", "signature_image", "sender_email", "recipient_email", "creation_date", "date_signature").filter(Q(recipient_email= email) | Q(sender_email= email)).filter(
            reduce(operator.and_, (Q(name__istartswith = q) |Q(name__icontains = q)|Q(description__icontains = q)|Q(sender_email__icontains = q)|Q(creation_date__icontains = q) for q in query_list)))

    return Response(list(queryset))

    if match:
        return HttpResponse(queryset, content_type='application/json')

    return HttpResponse('NOT MATCH')

@api_view(['POST'])
def post_document(request):
    if not authlib.check_authorize(request.session):
        return Response({'server response': "authentication required"}, status = status.HTTP_401_UNAUTHORIZED)

    if not request.method == 'POST':
        return Response(False)
    parser_classes = (FileUploadParser,)
    settings.LOGGER.debug(request.method)
    if request.method == 'PATCH' or request.method == 'POST':
        file_serializer = FileSerializer(
            Signature,
            data=request.data
        )
        settings.LOGGER.debug(file_serializer.is_valid())
        settings.LOGGER.debug(request.data['file'])

        email = authlib.get_jwt(request.session['access_token'])['email']
        name = authlib.get_jwt(request.session['access_token'])['name']
        signature = Signature()
        signature.document = request.data['file']
        signature.sender_email = email
        signature.recipient_email = request.data['emailDe']
        signature.creation_date = request.data['date']
        signature.name = request.data['name']
        signature.description = request.data['description']
        signature.save()
        # Send mail
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        settings.LOGGER.debug("server started")
        server.starttls()
        settings.LOGGER.debug("logging in")
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        settings.LOGGER.debug("logged in")
        message = 'Bonjour,<br /> <br/> Vous avez un document à signer de la part du: ' + name + '. <br /> Veuillez consulter votre compte : <a href="https://signature.chamberlab.net/">Signature</a> . <br /> <br /> Cordialement, <br /> CCI France.'
        settings.LOGGER.debug("sending")
        msg = EmailMultiAlternatives( "Document à signer", message, email, [request.data['emailDe']])
        msg.attach_alternative(message, "text/html")
        msg.send()
            
    return Response(True)


@api_view(['POST'])
def post_note_frais(request):
    if not authlib.check_authorize(request.session):
        return Response({'server response': "authentication required"}, status = status.HTTP_401_UNAUTHORIZED)

    if not request.method == 'POST':
        return Response(False)
    parser_classes = (FileUploadParser,)
    settings.LOGGER.debug(request.method)
    if request.method == 'PATCH' or request.method == 'POST':
        file_serializer = FileSerializer(
            Signature,
            data=request.data
        )
        settings.LOGGER.debug(file_serializer.is_valid())
        settings.LOGGER.debug(request.data['file'])
        email = authlib.get_jwt(request.session['access_token'])['email']
        name = authlib.get_jwt(request.session['access_token'])['name']
        signature = Signature()
        signature.document = request.data['file']
        signature.sender_email = email
        signature.creation_date = request.data['date']
        signature.name= request.data['name']
        signature.save() 
        # Send mail
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        settings.LOGGER.debug("server started")
        server.starttls()
        settings.LOGGER.debug("logging in")
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        settings.LOGGER.debug("logged in")
        message = 'Bonjour,<br /> Vous avez un document à signer de la part du: ' + name + '. <br /> Veuillez consulter votre compte: <a href="https://signature.chamberlab.net/">Signature</a>. <br /> <br /> Cordialement, <br /> CCI France.'
        settings.LOGGER.debug("sending")
        msg = EmailMultiAlternatives( "Note de frais a signer", message, email, ["ichrak.ladhari21@gmail.com"])
        msg.attach_alternative(message, "text/html")
        msg.send()
    return Response(True)

@api_view(['POST','GET'])
def send_messages(request):
    settings.LOGGER.debug("starting server")
    email = authlib.get_jwt(request.session['access_token'])['email']
    name = authlib.get_jwt(request.session['access_token'])['name']
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    settings.LOGGER.debug("server started")
    server.starttls()
    settings.LOGGER.debug("logging in")
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    settings.LOGGER.debug("logged in")
    message = 'Bonjour,<br /> le document a été signé . <br /> Veuillez consulter votre compte : <a href="https://signature.chamberlab.net/">Signature</a>. <br /> <br /> Cordialement, <br /> CCI France.'
    settings.LOGGER.debug("sending")
    msg = EmailMultiAlternatives( "Document signer", message, email, ["ichrak.ladhari21@gmail.com"])
    msg.attach_alternative(message, "text/html")
    msg.send()
    settings.LOGGER.debug("sent")

    return Response(message)


