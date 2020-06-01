import json
from django import forms
import rest_framework

from referentiels.api import serializers
from .models import Personnel


class PostForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = "__all__"

class CFEAdminForm(forms.ModelForm):
    def clean_code(self):
        try:
            # Pour la validation utilisation de la même méthode que pour la
            # sérialisation fin de mutualiser le code
            serializers.CFESerializer.static_validate(self.data)
        except rest_framework.serializers.ValidationError as msg:
            # Lever une exception de type ValidationError pour un affichage
            # intégré dans le formulaire
            error = msg.get_full_details()['code']['message']
            raise forms.ValidationError(error)
        return self.cleaned_data["code"]
