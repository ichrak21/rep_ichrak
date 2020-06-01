from django.db import models
import reversion
# Create your models here.

class CCI(models.Model):
    
    """ Modèle de données pour les CCI """

    actif = models.BooleanField(default=True)
    code = models.IntegerField()
    id_cci = models.IntegerField(default=0)
    courriel = models.EmailField(max_length=255, blank=True, default='')
    date_creation = models.DateField(null=True)
    fax = models.CharField(max_length=50, blank=True, default='')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    nom = models.CharField(max_length=100)
    siret = models.CharField(max_length=14, blank=True, default='')
    telephone = models.CharField(max_length=50, blank=True, default='')
    type = models.CharField(max_length=10)
    url_logo = models.URLField(max_length=255, blank=True, default='')
    url_site_web = models.URLField(max_length=255, blank=True, default='')
    pays = models.ForeignKey('Pays', related_name='ccis', on_delete=models.SET_NULL, blank=True, null=True)
    region = models.ForeignKey('Region', related_name='ccis', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        """ Libellé affiché sur les listes """
        return '%d : %s' % (self.code, self.nom)

    class Meta:
        """ Tri des listes par défaut """
        ordering = ['code', 'nom']


#    logo                   = models.ImageField(blank=True)

#    version_referentiel_id = models.IntegerField()
#    ville_du_siege         = models.CharField(max_length=100)
#    tauxtva                = models.FloatField()
#    id                     = models.AutoField(primary_key=True)
#    cci_mere_id            = models.IntegerField(blank=True)
#    code_comptable         = models.CharField(max_length=7)

@reversion.register()
class CFE(models.Model):
    """ Modèle de données pour les CFE """
    TYPES_CFE = (
        ('C', 'CCI'),
        ('U', 'URSSAF'),
        ('G', 'GREFFE'),
    )

    actif = models.BooleanField(default=True)
    code = models.CharField(max_length=5)
    courriel = models.EmailField(max_length=255, blank=True, default='')
    libelle = models.CharField(max_length=120)
    libelle_court = models.CharField(max_length=50, blank=True, default='')
    type_cfe = models.CharField(max_length=1, choices=TYPES_CFE)
    telephone = models.CharField(max_length=50, blank=True, default='')
    fax = models.CharField(max_length=50, blank=True, default='')
    url_logo = models.URLField(max_length=255, blank=True, default='')
    url_site_web = models.URLField(max_length=255, blank=True, default='')
    cci = models.ForeignKey(CCI, related_name='cfes', on_delete=models.CASCADE, blank=True, null=True)

    pays = models.ForeignKey('Pays', related_name='cfes', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        """ Libellé affiché sur les listes """
        return '%s : %s' % (self.code, self.libelle)

    class Meta:
        """ Tri des listes par défaut """
        ordering = ['code', 'libelle']


class Adresse(models.Model):
    """ Modèle de données pour représenter les adresses """
    TYPES_ADRESSE = (
        ('P', 'Adresse postale'),
        ('F', 'Adresse de facturation'),
    )

    actif = models.BooleanField(default=True)
    code_postal = models.CharField(max_length=5, blank=True, default='')
    commune = models.CharField(max_length=100, blank=True, default='')
    complement = models.CharField(max_length=100, blank=True, default='')
    distribution_speciale = models.CharField(max_length=100, blank=True, default='')
    indice_repetition = models.CharField(max_length=10, blank=True, default='')
    nom_voie = models.CharField(max_length=100, blank=True, default='')
    numero_voie = models.CharField(max_length=20, blank=True, default='')
    type_adresse = models.CharField(max_length=1, choices=TYPES_ADRESSE, default='P')
    type_voie = models.CharField(max_length=20, blank=True, default='')

    cci = models.ForeignKey(CCI, related_name="adresses", on_delete=models.CASCADE, blank=True, null=True)
    cfe = models.ForeignKey(CFE, related_name="adresses", on_delete=models.CASCADE, blank=True, null=True)


class Personne(models.Model):
    """ Modèle de données pour les personnes """

    civilite = models.CharField(max_length=20, blank=True, default='')
    code = models.CharField(max_length=50)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)

    def __str__(self):
        return '%s : %s %s' % (self.code, self.nom, self.prenom)


class Qualite(models.Model):
    """ Modèle de données pour les qualites des personnes """

    code = models.CharField(max_length=10)
    libelle = models.CharField(max_length=50)

    def __str__(self):
        return '%s : %s' % (self.code, self.libelle)


class Responsabilite(models.Model):
    """ Modèle de données pour les responsabilités des personnes """

    actif = models.BooleanField(default=True)
    cci = models.ForeignKey(CCI, related_name="responsabilites", on_delete=models.CASCADE, blank=True, null=True)
    personne = models.ForeignKey(Personne, related_name="responsabilites", on_delete=models.CASCADE, blank=True,
                                 null=True)
    qualite = models.ForeignKey(Qualite, related_name="responsabilites", on_delete=models.CASCADE, blank=True,
                                null=True)
    signature = models.CharField(max_length=255, blank=True, default='')


## Référentiel géographique

@reversion.register()
class Continent(models.Model):
    """ Modèle de données pour les continents """

    actif = models.BooleanField(default=True)
    code = models.CharField(max_length=2)
    libelle = models.CharField(max_length=100)

    def __str__(self):
        """ Libellé affiché sur les listes """
        return '%s : %s' % (self.code, self.libelle)

    class Meta:
        """ Tri des listes par défaut """
        ordering = ['code', 'libelle']


class Pays(models.Model):
    """ Modèle de données pour les pays """

    actif = models.BooleanField(default=True)
    ancien_nom = models.CharField(max_length=100, blank=True, default='')
    annee_inde = models.IntegerField(blank=True, null=True)
    code_actualite = models.IntegerField(blank=True, null=True)
    code_ancien_pays = models.CharField(max_length=5, blank=True, default='')
    codecfe = models.CharField(max_length=3, blank=True, default='')
    codeiso2 = models.CharField(max_length=2, blank=True, default='')
    codeiso3 = models.CharField(max_length=3, blank=True, default='')
    code_num3 = models.IntegerField()
    code_officiel_geo = models.CharField(max_length=5, blank=True, default='')
    code_pays_ratt = models.CharField(max_length=5, blank=True, default='')
    esteee = models.BooleanField()
    estue = models.BooleanField()
    libelle = models.CharField(max_length=100)
    libelle_complet = models.CharField(max_length=100, blank=True, default='')
    nationalite = models.CharField(max_length=100, blank=True, default='')
    continent = models.ForeignKey(Continent, related_name='pays', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        """ Libellé affiché sur les listes """
        return '%d : %s' % (self.code_num3, self.libelle)

    class Meta:
        """ Tri des listes par défaut """
        ordering = ['libelle']


@reversion.register()

class Region(models.Model):
    """ Modèle de données pour les régions """

    actif = models.BooleanField(default=True)
    code = models.CharField(max_length=2, blank=True, default='')
    code_consulaire = models.CharField(max_length=2)
    libelle = models.CharField(max_length=100)

    def __str__(self):
        """ Libellé affiché sur les listes """
        return '%s : %s' % (self.code_consulaire, self.libelle)

    class Meta:
        """ Tri des listes par défaut """
        ordering = ['libelle']


@reversion.register()

class Departement(models.Model):
    """ Modèle de données pour les départements """

    actif = models.BooleanField(default=True)
    code = models.CharField(max_length=3)
    libelle = models.CharField(max_length=100)

    region = models.ForeignKey(Region, related_name="departements", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        """ Libellé affiché sur les listes """
        return '%s : %s' % (self.code, self.libelle)

    class Meta:
        """ Tri des listes par défaut """
        ordering = ['code']


@reversion.register()

class Commune(models.Model):

    """ Modèle de données pour les communes """

    actif = models.BooleanField(default=True)
    article = models.CharField(max_length=10, blank=True, default='')
    code = models.CharField(max_length=5)
    libelle = models.CharField(max_length=100)

    cci = models.ForeignKey(CCI, related_name="communes", on_delete=models.SET_NULL, blank=True, null=True)
    cfe = models.ForeignKey(CFE, related_name="communes", on_delete=models.SET_NULL, blank=True, null=True)
    departement = models.ForeignKey(Departement, related_name="communes", on_delete=models.SET_NULL, blank=True,
                                    null=True)

    def __str__(self):
        """ Libellé affiché sur les listes """
        return '%s : %s' % (self.code, self.libelle)

    class Meta:
        """ Tri des listes par défaut """
        ordering = ['code', 'libelle']


class CodePostal(models.Model):
    """ Modèle de données pour les codes postaux """

    actif = models.BooleanField(default=True)
    code = models.CharField(max_length=5)

    class Meta:
        """ Tri des listes par défaut """
        ordering = ['code']

    def __str__(self):
        """ Libellé affiché sur les listes """
        return '%s' % self.code


class Acheminement(models.Model):
    """ Modèle de données pour les libellés de code postaux (acheminement) """

    actif = models.BooleanField(default=True)
    libelle = models.CharField(max_length=100)

    code_postal = models.ForeignKey(CodePostal, related_name="acheminements", on_delete=models.SET_NULL, blank=True,
                                    null=True)
    commune = models.ForeignKey(Commune, related_name="acheminements", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        """ Libellé affiché sur les listes """
        return '%s' % (self.libelle)

    class Meta:
        """ Tri des listes par défaut """

        ordering = ['libelle']
        indexes = [
            models.Index(fields=['id'], name='acheminements_id_1'),
            models.Index(fields=['-id'], name='acheminements_id_2'),
            models.Index(fields=['libelle'], name='acheminements_libelle_1'),
            models.Index(fields=['-libelle'], name='acheminements_libelle_2')
        ]




class Personnel(models.Model):

    """ Modèle de données pour les personnels """

    civilite = models.CharField(max_length=100, blank=True, default='')
    prenom = models.CharField(max_length=100, blank=True, default='')
    nom = models.CharField(max_length=100,blank=True, null=True)
    direction= models.CharField(max_length=100,blank=True, null=True)
    fonction_generique = models.CharField(max_length=100, blank=True, default='')
    fonction_exacte = models.CharField(max_length= 1000, blank=True, default='')
    date_debut_fonction = models.CharField(max_length=30, blank=True, default='')
    date_fin_fonction = models.CharField(max_length=30, blank=True, default='')
    titre_politesse = models.CharField(max_length=30, blank=True, default='')
    email = models.EmailField(max_length=255, blank=True, default='')
    tel_fixe = models.CharField(max_length=150, blank=True, default='')
    tel_mobile = models.CharField(max_length=150, blank=True, default='')
    service = models.CharField(max_length=100, blank=True, default='')
    expertise = models.CharField(max_length=100, blank=True, default='')
    domaine_metier= models.CharField(max_length=100, blank=True, default='')
    centres = models.CharField(max_length=100, blank= True)
    raison_sociale = models.CharField(max_length=100, blank=True, default='')
    n_siret = models.CharField(max_length=30, blank=True, default='')
    adress = models.CharField(max_length=100, blank=True, default='')
    complement_adresse = models.CharField(max_length=100, blank= True)
    BP = models.CharField(max_length=100, blank=True, default='')
    CP = models.CharField(max_length=10,  blank=True, default='')
    ville = models.CharField(max_length=100, blank=True, default='')
    pays = models.CharField(max_length=100, blank= True)
    phone = models.CharField(max_length=150, blank=True, default='')
    fax = models.CharField(max_length=100, blank=True, default='')
    site = models.CharField(max_length=100, blank=True, default='')
    type_organisme = models.CharField(max_length=100, blank=True, default='')
    enseigne= models.CharField(max_length=100, blank=True, default='')
    sous_type = models.CharField(max_length=100, blank= True)
    secteur_activite = models.CharField(max_length=100, blank=True, default='')
    Code_APE = models.CharField(max_length=100, blank= True)
    effectif = models.CharField(max_length=100, blank= True)
    nombre_ressortissants = models.CharField(max_length=100, blank=True, default='')
    id_annuaire = models.CharField(max_length=100, blank=True, default='')
    source_import = models.CharField(max_length=100, blank= True)
    region = models.CharField(max_length=100, blank=True, default='')
    departement = models.CharField(max_length=100, blank=True, default='')
    linkedin = models.CharField(max_length=100, blank=True, default='')
    facebook = models.CharField(max_length=100, blank=True, default='')
    tweeter= models.CharField(max_length=100, blank=True, default='')
    radiation= models.CharField(max_length=100, blank=True, default='')
    matricule = models.CharField(max_length=100, blank=False)

    def __str__(self):

        """ Libellé affiché sur les listes """  

        return '%s %s : %s' % (self.prenom, self.nom, self.matricule)

    class Meta:

        """ Tri des listes par défaut, tri par matricule  """
        ordering = ['matricule']
        indexes = [
            models.Index(fields=['prenom'], name='personnels_prenom'),
            models.Index(fields=['nom'], name='personnels_nom'),
            models.Index(fields=['email'], name='personnels_email'),
            models.Index(fields=['phone'], name='personnels_phone'),
            models.Index(fields=['fonction_exacte'], name='personnels_fonction_exacte'),
            models.Index(fields=['matricule'], name='personnels_matricule'),
            models.Index(fields=['raison_sociale'], name='personnels_raison_sociale')
        ]






