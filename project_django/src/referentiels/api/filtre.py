from referentiels.api.models import Personnel
import django_filters
class UserFilter(django_filters.FilterSet):
    class Meta:
        model = Personnel
        fields = ['email', 'matricule', 'nom', 'prenom' ]

