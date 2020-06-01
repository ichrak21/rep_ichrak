from django.db import models
from django.conf import settings

class Signature(models.Model):
    
    """ Modèle de données pour les Signature """

    name = models.CharField(max_length=100,blank=True, default='')
    description = models.TextField(blank=True, default='')
    document = models.FileField(upload_to='signature')
    signature_image = models.TextField(blank=True, default='')
    sender_email = models.EmailField(max_length=255, blank=True, default='')
    recipient_email = models.EmailField(max_length=255, blank=True, default='')
    full_name_sender = models.CharField(max_length=100,blank=True, default='')
    full_name_recipient = models.CharField(max_length=100,blank=True, default='')
    creation_date = models.DateField(null=True,blank=True)
    date_signature = models.DateField(null=True,blank=True)

    def __str__(self):
        """ Libellé affiché sur les listes """
        return '%s : %s' % (self.name, self.description)

    class Meta:
        """ Tri des listes par défaut """
        ordering = ['name']
