from django.contrib.auth.models import User, Group
from rest_framework import serializers
from referentiels.api import models


class PaysCCISerializer(serializers.ModelSerializer):
    """ Sérialisation du pays pour le service CCI """

    class Meta:
        model = models.Pays
        fields = ('libelle', 'actif')


class RegionCCISerializer(serializers.ModelSerializer):
    """ Sérialisation de la région pour le service CCI """

    class Meta:
        model = models.Region
        fields = ('libelle', 'actif')


class AdresseSerializer(serializers.ModelSerializer):
    """ Sérialisation des adresses """

    class Meta:
        model = models.Adresse
        exclude = ('id', 'cci', 'cfe')


class PersonneSerializer(serializers.ModelSerializer):
    """ Sérialisation pour les données des personnes """

    class Meta:
        model = models.Personne
        exclude = ('id', 'code')


class ResponsabiliteSerializer(serializers.ModelSerializer):
    """ Sérialisation pour les responsabilités """
    personne = PersonneSerializer()
    qualite = serializers.SlugRelatedField(
        read_only=True,
        slug_field='libelle'
    )

    class Meta:
        model = models.Responsabilite
        exclude = ('id', 'cci')


class CCISerializer(serializers.ModelSerializer):
    """ Sérialisation pour les données CCI """
    pays = PaysCCISerializer(read_only=True)
    region = RegionCCISerializer(read_only=True)
    adresses = AdresseSerializer(many=True, read_only=True)
    responsabilites = ResponsabiliteSerializer(many=True, read_only=True)

    class Meta:
        model = models.CCI
        fields = ('id', 'nom', 'code', 'siret', 'courriel', 'url_site_web', 'telephone', 'fax', 'date_creation',
                  'url_logo', 'pays', 'region', 'adresses', 'responsabilites')


class CCISmallSerializer(serializers.ModelSerializer):
    """ Sérialisation pour les données CCI minifié """

    class Meta:
        model = models.CCI
        fields = ('id', 'nom', 'code', 'actif')


class CFESerializer(serializers.ModelSerializer):
    """ Sérialisation pour les données CFE """

    # Personnalisation de la relation cci avec CCISmallSerializer
    # https://www.django-rest-framework.org/api-guide/relations/#custom-relational-fields
    cci = CCISmallSerializer(read_only=True)
    pays = PaysCCISerializer(read_only=True)
    adresses = AdresseSerializer(many=True, read_only=True)

    class Meta:
        model = models.CFE
        fields = '__all__'

    def validate_code(self, value):
        if (value[0] not in [typ for typ, lib in models.CFE.TYPES_CFE]):
            raise serializers.ValidationError('This field should start with a valid type_cfe')
        return value

    def validate(self, data):
        return CFESerializer.static_validate(data)

    def static_validate(data):
        """ """
        if data['type_cfe'] != data['code'][0]:
            raise serializers.ValidationError({'code': 'This field should start with type_cfe'})
        return data


class ContinentSerializer(serializers.ModelSerializer):
    """ Sérialisation pour les données Continents """

    class Meta:
        model = models.Continent
        fields = '__all__'


class PaysSerializer(serializers.ModelSerializer):
    """ Sérialisation pour les données Pays """

    # Affichage du code à la place de l'identifiant interne
    # https://www.django-rest-framework.org/api-guide/relations/#slugrelatedfield
    continent = serializers.SlugRelatedField(
        read_only=True,
        slug_field='code'
    )

    class Meta:
        model = models.Pays
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    """ Sérialisation pour les données Régions """

    class Meta:
        model = models.Region
        fields = '__all__'


class DepartementSerializer(serializers.ModelSerializer):
    """ Sérialisation pour les Départements """

    class Meta:
        model = models.Departement
        fields = '__all__'


class AcheminementSerializer(serializers.ModelSerializer):
    """ Sérialisation pour les acheminements """
    commune = serializers.SlugRelatedField(
        read_only=True,
        slug_field='code'
    )

    class Meta:
        model = models.Acheminement
        exclude = ('id', 'code_postal',)


class AcheminementCommuneSerializer(serializers.ModelSerializer):
    """ Sérialisation des acheminements utilisée par le service commune """
    code_postal = serializers.SlugRelatedField(
        read_only=True,
        slug_field='code'
    )

    class Meta:
        model = models.Acheminement
        fields = ('libelle', 'code_postal')


class CommuneSerializer(serializers.ModelSerializer):
    """ Sérialisation pour les communes """
    acheminements = AcheminementCommuneSerializer(many=True, read_only=True)

    class Meta:
        model = models.Commune
        exclude = ('id', 'cci', 'cfe', 'departement')


class CodePostalSerializer(serializers.ModelSerializer):
    """ Sérialisation pour les codes postaux """
    acheminements = AcheminementSerializer(many=True, read_only=True)

    class Meta:
        model = models.CodePostal
        exclude = ('id',)
