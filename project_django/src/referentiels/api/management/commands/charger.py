from django.core.management.base import BaseCommand
import reversion
import pandas
from referentiels.api import models
from referentiels.api.management import charger_pays, charger_communes, \
    charger_cci, charger_cfe


class Command(BaseCommand):
    help = 'Import des sources depuis les fichiers de référence INSEE, CFE, etc.'

    def __init__(self, *args, **kw):
        BaseCommand.__init__(self, *args, **kw)
        self.nbUpdate = 0
        self.nbCreate = 0
        self.nbDelete = 0

    def add_arguments(self, parser):
        parser.add_argument('[tables]', nargs='+', type=str,
                            help='Référentiel à charger : Pays pour charger Continent et Pays, '
                                 'Communes pour charger Région, Département et Commune')

    def handle(self, *args, **options):
        """ Méthode appelé en entrée par le gestionnaire de commande """
        pandas.options.mode.chained_assignment = None
        for ref in options['[tables]']:
            # Vérifier si le modèle existe
            model = getattr(models, ref, None)
            if model:
                # Appeler la méthode de chargement correspondant au référentiel 'ref'
                self.nbUpdate = 0
                self.nbDelete = 0
                self.nbCreate = 0
                action = getattr(self, "charger" + ref)
                action()
            else:
                self.stdout.write("{} n'existe pas".format(ref))

    def getObject(self, model, **kw):
        """ Retourne l'objet correspondant au model model et au filtre passé avec kw 
        par exemple getObject(models.CFE, code='C7501') retournera le **CFE** ayant le code *C7501*
        retourne None si aucune correspondance n'a été trouvé
        """
        try:
            return model.objects.get(**kw)
        except Exception:
            return None

    def createObject(self, model, serie):
        """ Création d'un objet de type model (models.*) avec les données de
        serie qui est une instance de 'pandas.Series'
        http://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html
        chaque index de l'objet serie doit correspondre aux attributs de l'objet model
        """
        obj = None
        if not serie.empty:
            obj = model()
            for ci in serie.index:
                value = serie[ci]
                if isinstance(value, bool):
                    setattr(obj, ci, value)
                elif value:
                    setattr(obj, ci, value)
            # Le commit des mise à jour fonctionnement également dans cette
            # méthode dans la fonction mais dans ce cas la
            # stacktrace est moins lisible
            # obj.save()
            # self.nbCreate += 1
            # 
            return obj

    def updateObject(self, obj, df):
        """ Réalise la mise à jour de l'objet 'obj' à partir de la ligne de
        dataframe 'dt'. La mise à jour est faite attribut par attribut
        uniquement si la valeur est différente de la précédente. Le nom des
        attributs du dataframe et du model doivent donc correspondre.
        
        retourne Vrai si une mise à jour a été effectuée faut dans le cas
        contraire
        """
        update = False
        for ci in list(df.columns.values):
            value = df[ci].values[0]
            if value and getattr(obj, ci) != value:
                setattr(obj, ci, value)
                update = True

        return update

    def chargerPays(self):
        """ Applique la mise à jour pour le chargement des Pays et des Continents """
        # XXX Gérer supprimer lien direct vers les fichiers
        data_pays = charger_pays.construireDataframePays('referentiels/api/management/fichiers/pays2016.txt',
                                                         'referentiels/api/management/fichiers/cfenet_pays.csv')
        # Remplir les années vide 
        data_pays['annee_inde'] = data_pays['annee_inde'].fillna('')
        data_continent = charger_pays.construireDataframeContinent(
            'referentiels/api/management/fichiers/continents.xls')
        self.metaChargement(models.Continent, data_continent, 'Continent(s)')
        # Jointure entre les pays et les continents
        data_pays['continent'] = data_pays['continent'].apply(lambda x: self.getObject(models.Continent, code=x))
        self.metaChargement(models.Pays, data_pays, 'Pays', 'codeiso3')

    def chargerRegion(self):
        """ Charger le référentiel des régions """
        # XXX chemin du referentiel
        data_region = charger_communes.construireDataframeRegion('referentiels/api/management/fichiers/region2019.csv')
        self.metaChargement(models.Region, data_region, 'Région(s)')

    def chargerDepartement(self):
        """ Charger le référentiel des départements en réalisant la jointure
        avec les régions à appeler après le chargement de la table Region 
        """
        data_departement = charger_communes.construireDataframeDepartement(
            'referentiels/api/management/fichiers/departement2019.csv')
        # Jointure avec les régions
        data_departement['region'] = data_departement['reg'].apply(lambda x: self.getObject(models.Region, code=x))
        data_departement = data_departement.drop(['reg'], axis=1)
        self.metaChargement(models.Departement, data_departement, 'Département(s)')

    def chargerCommune(self):
        """ Charger le référentiel des communes à lancer après le chargement
        des départements, CCI et CFE
        """
        data_commune = charger_communes.construireDataframeCommune(
            'referentiels/api/management/fichiers/commune2019.csv')
        ## Jointure avec les département
        data_commune['departement'] = data_commune['dep'].apply(lambda x: self.getObject(models.Departement, code=x))
        data_commune = data_commune.drop(['dep'], axis=1)
        data_correspondance = charger_communes.construireDataframeCorrespondanceCommune(
            'referentiels/api/management/fichiers/correspondance_communes_cfe_cci_avec_com.csv')
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
        # jointuer sur la colonne 'code' 
        data_commune = data_commune.merge(data_correspondance, on='code')
        data_commune['cci'] = data_commune['id_cci'].apply(lambda x: self.getObject(models.CCI, id_cci=x))
        data_commune = data_commune.drop(['id_cci'], axis=1)
        data_commune['cfe'] = data_commune['code_cfe'].apply(lambda x: self.getObject(models.CFE, code=x))
        data_commune = data_commune.drop(['code_cfe'], axis=1)

        self.metaChargement(models.Commune, data_commune, 'Commune(s)')

    def chargerCodePostal(self):
        """ Chargé le référentiel des codes postaux et de la table Acheminement
        à appeler après le chargement des communes
        """
        data_laposte = charger_communes.construireDataframeLaposte(
            'referentiels/api/management/fichiers/laposte_hexasmal_6.31_12.0.csv')
        # Préparation du dataframe des codes postaux pour le chargement de la table CodePostail (code, actif)
        data_codesPostaux = pandas.DataFrame(data_laposte['code_postal'].unique(), columns=['code'])
        # Appliquer le chargement
        self.metaChargement(models.CodePostal, data_codesPostaux, 'codes postaux')
        # Préparation du dataframe des acheminements pour le chargement de la table Acheminement (actif, libelle,
        # CodePostal, Commune) Jointure avec les communes
        data_laposte['commune'] = data_laposte['code_commune'].apply(lambda x: self.getObject(models.Commune, code=x))
        # Jointure des codes postaux
        data_laposte['code_postal'] = data_laposte['code_postal'].apply(
            lambda x: self.getObject(models.CodePostal, code=x))
        # Supprimer la colonne code_commune
        data_laposte = data_laposte.drop(['code_commune'], axis=1)
        # Appliquer le chargement
        self.metaChargement(models.Acheminement, data_laposte, 'Acheminement(s)', 'libelle')

    def chargerQualite(self):
        """ Charger le référentiel des qualités """
        data_qualite = charger_cci.construireDataframeQualite('referentiels/api/management/fichiers/qualite.csv')
        self.metaChargement(models.Qualite, data_qualite, 'Qualite(s)', 'code')

    def chargerCCI(self):
        """ Charge le référentiel des CCI et les dépendances (adresse,
        president, directeur), à appeler après le chargement des continents et
        des régions """
        data = charger_cci.construireDataframeCCI('referentiels/api/management/fichiers/cci.xls')
        data_cci = data['cci']
        # Jointure pour les régions
        data_cci['region'] = data_cci['code_region'].apply(lambda x: self.getObject(models.Region, code=x))
        # Jointure pour les pays
        data_cci['pays'] = self.getObject(models.Pays, libelle="FRANCE")
        data_cci = data_cci.drop(['code_region'], axis=1)
        data_cci = data_cci.drop(['code_region_cci'], axis=1)
        data_cci = data_cci[data_cci['code'] != '']
        self.metaChargement(models.CCI, data_cci, "CCI", 'id_cci')

        # Mise à jour de l'adresse
        data_adresse = data['adresse']
        data_adresse['cci'] = data_adresse['id_cci'].apply(lambda x: x and self.getObject(models.CCI, id_cci=x))
        # Conserver uniquement les adresses rattachées à une CCI
        data_adresse = data_adresse[~data_adresse.cci.isnull()]
        # Supprimer la colonne id_cci 
        data_adresse = data_adresse.drop(['id_cci'], axis=1)
        self.metaChargement(models.Adresse, data_adresse, "adresse(s)", 'cci', supprimer=False)
        for obj in models.Adresse.objects.exclude(cci=None):  # parcourir les données en base
            f = data_adresse.loc[data_adresse["cci"] == obj.cci]
            if f.empty:
                obj.delete()
                self.nbDelete += 1
        self.stdout.write('{} supprimée(s) {}'.format("Adresse CCI", self.nbDelete))

        # Mise à jour des président
        data_president = data_responsabilitePRE = data['president']
        data_president = data_president.drop(['id_cci'], axis=1)
        # Mise à jour des directeurs
        data_directeur = data_responsabiliteDIR = data['directeur']
        data_directeur = data_directeur.drop(['id_cci'], axis=1)
        data_personne = pandas.concat([data_president, data_directeur])
        data_personne = data_personne.drop_duplicates(subset=['code'])
        self.metaChargement(models.Personne, data_personne, "Personne", 'code')

        # Chargement des responsabilité
        data_responsabilitePRE = data_responsabilitePRE[~data_responsabilitePRE.nom.isnull()]
        data_responsabilitePRE['cci'] = data_responsabilitePRE['id_cci'].apply(
            lambda x: x and self.getObject(models.CCI, id_cci=x))
        data_responsabilitePRE = data_responsabilitePRE.drop(['id_cci'], axis=1)
        data_responsabilitePRE['qualite'] = self.getObject(models.Qualite, code='P')
        data_responsabilitePRE['personne'] = data_responsabilitePRE['code'].apply(
            lambda x: self.getObject(models.Personne, code=x))
        data_responsabilitePRE = data_responsabilitePRE.drop(['code', 'nom', 'prenom'], axis=1)

        # Chargement des responsabilité
        data_responsabiliteDIR = data_responsabiliteDIR[~data_responsabiliteDIR.nom.isnull()]
        data_responsabiliteDIR['cci'] = data_responsabiliteDIR['id_cci'].apply(
            lambda x: x and self.getObject(models.CCI, id_cci=x))
        data_responsabiliteDIR = data_responsabiliteDIR.drop(['id_cci'], axis=1)
        data_responsabiliteDIR['qualite'] = self.getObject(models.Qualite, code='D')
        data_responsabiliteDIR['personne'] = data_responsabiliteDIR['code'].apply(
            lambda x: self.getObject(models.Personne, code=x))
        data_responsabiliteDIR = data_responsabiliteDIR.drop(['code', 'nom', 'prenom'], axis=1)
        data_responsabilite = pandas.concat([data_responsabilitePRE, data_responsabiliteDIR])
        self.metaChargement(models.Responsabilite, data_responsabilite, "Responsabilite(s)", 'personne')

    def chargerCFE(self):
        """ Charge le référentiel des CFE et les dépendances (adresse) """
        data = charger_cfe.construireDataframeCFE('./referentiels/api/management/fichiers/cfe.xls')
        data_cfe = data['cfe']
        self.metaChargement(models.CFE, data_cfe, 'CFE(s)', 'code')

        data_adresse = data['adresse']
        data_adresse['cfe'] = data_adresse['code'].apply(lambda x: self.getObject(models.CFE, code=x))
        # Ajout du libellé de la commune en deux temps : via le dataframe
        data_commune = charger_communes.construireDataframeCommune(
            'referentiels/api/management/fichiers/commune2019.csv')
        data_adresse['commune'] = data_adresse['code_commune'].apply(lambda x: data_commune.loc[data_commune.code == x])
        data_adresse['commune'] = data_adresse['commune'].apply(lambda x: not x.empty and x.libelle.values[0] or '')

        # Supprimer les colonnes techniques inutiles
        data_adresse = data_adresse.drop(['code_commune', 'code'], axis=1)
        self.metaChargement(models.Adresse, data_adresse, 'Adresse(s) CFE', 'cfe', supprimer=False)
        for obj in models.Adresse.objects.exclude(cfe=None):  # parcourir les données en base
            f = data_adresse.loc[data_adresse["cfe"] == obj.cfe]
            if f.empty:
                obj.delete()
                self.nbDelete += 1
        self.stdout.write('{} supprimée(s) {}'.format("Adresse CFE", self.nbDelete))

        # Ajouter la correspondance cci
        for obj in models.CFE.objects.all():  # parcourir les données en base
            communes = models.Commune.objects.filter(cfe=obj).order_by('cci__id').select_related('cci')
            if communes:
                obj.cci = communes[0].cci
                obj.save()
        self.stdout.write('Correspondance CCI/CFE mise à jour')

    def metaChargement(self, model, dataframe, nom, cle_primaire="code", supprimer=True):
        """
        Réalise le chargement des données en base à partir du dataframe
        `dataframe' dans le model de données `model`. 

        La colonne 'cle_primaire' (code par défaut) est utilisé comme clé pour
        identifier les donner à mettre à jour

        @param model : Instance de referentiels.api.models.*
        @param dataframe : Instance de pandas.dataframe
        @param nom : nom utilisé a des fins de journalisation
        @param supprimer: indique s'il faut supprimer les données non rattachées
        """
        self.nbUpdate = 0
        self.nbCreate = 0
        self.nbDelete = 0
        # Créer une révision 
        for obj in model.objects.all():  # parcourir les données en base
            with reversion.create_revision():
                f = dataframe.loc[dataframe[cle_primaire] == getattr(obj, cle_primaire)]  #
                if not f.empty:  # si existe dans dataframe alors verfier s'il faut faire une mise à jour
                    updated = self.updateObject(obj, f)
                    if updated:  # Si mise à jour sauvegarder et incrémenté le compteur
                        obj.save()
                        self.nbUpdate += 1
                elif supprimer:  # sinon supprimer de la base de données
                    obj.delete()
                    self.nbDelete += 1
                reversion.set_comment("Mise a jour shell")

        # Création des nouvelles entrées, la colonne exist permet de filtrer les nouvelles entrées
        dataframe['exist'] = dataframe[cle_primaire].apply(
            lambda x: self.getObject(model, **{cle_primaire: x}) is not None
        )
        # Le dataframe new_data contient uniquement les nouvelles entrées
        new_data = dataframe.loc[dataframe['exist'] == False]

        # Supprimer la colonne exist
        new_data = new_data.drop(['exist'], axis=1)
        # Créer les nouvelles entrées pour chaque ligne du dataframe new_data
        new_objects = new_data.apply(lambda serie: self.createObject(model, serie), axis=1)
        # Le commit des mise à jour fonctionnement également lorsqu'on le
        # réalise dans la fonction createObject mais en cas de d'erreur la
        # stacktrace est moins lisible dans ce cas donc c'est ici:
        for obj in new_objects:
            with reversion.create_revision():
                obj.save()
                self.nbCreate += 1
                reversion.set_comment("Mise a jour shell")

        if supprimer:
            self.stdout.write(
                '{} mise(s) à jour {}, créée(s) {}, supprimée(s) {}'.format(nom, self.nbUpdate, self.nbCreate,
                                                                            self.nbDelete))
        else:
            self.stdout.write('{} mise(s) à jour {}, créée(s) {}'.format(nom, self.nbUpdate, self.nbCreate))
