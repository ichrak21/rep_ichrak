#!/usr/bin/env python3
"""
Prépare les fichiers pour le chargement en base de données via l'ORM de Django
"""
from collections import OrderedDict
import pandas
import datetime

mapping_cci = OrderedDict({
    'Id': 'id_cci',
    'code CCI': 'code',
    'Nom': 'nom',
    'active': 'actif',
    'CCI de rattachement': 'unused_cci_mere',
    'CCI de rattachement (ID)': 'unused_cci_mere_id',
    'remarque': 'unused_remarque',
    'ancien nom': 'unused_ancien_nom',
    'Pays': 'unused_pays',
    'code région INSEE': 'code_region',
    'code région CCI': 'code_region_cci',
    'Régions consulaire': 'unused_region_consulaire',
    'Régions administrative': 'unused_region_administrative',
    'Nom 2': 'unused_nom',
    'Type': 'type',
    'Nom alpha': 'unused_nom_alpha',
    'Date de création': 'date_creation',
    'Ville siège': 'unused_ville_siege',
    'SIRET': 'siret',
    'Téléphone': 'telephone',
    'Fax': 'fax',
    'Courriel contact': 'courriel',
    'URL Logo': 'url_logo',
    'Site web': 'url_site_web',
    'Longitude': 'longitude',
    'Latitude': 'latitude',
    'Localisation': 'unused_localisation',
    'Directeur Prénom': 'directeur_prenom',
    'Directeur Nom': 'directeur_nom',
    'Président prénom': 'president_prenom',
    'Président Nom': 'president_nom',
    'Numéro de voie': 'adresse_numero_voie',
    'indice de répétition': 'adresse_indice_repetition',
    'Type de voie': 'adresse_type_voie',
    'Nom de voie': 'adresse_nom_voie',
    'Complément de voie': 'adresse_complement_voie',
    'distribution spéciale': 'adresse_distribution_speciale',
    'Code postal': 'adresse_code_postal',
    'Commune': 'adresse_commune',
    'Taux TVA': 'unused_taux_tva',
    'Code comptable': 'unused_code_comptable',
    'directeur adresse mail': 'unused_directeur_courriel',
    'président date de naissance': 'unused_president_date_naissance',
    'codePresident': 'president_code',
    'codeDirecteur': 'directeur_code',
})


def construireDataframeCCI(p_fichier):
    """
    Retourne les dataframes (cci, adresse, president, directeur) pour le chargement de la table des CCI à partir du nom de fichier **p_fichier**
    """
    data_cci = pandas.read_excel(p_fichier, sheet_name='CCI', names=mapping_cci.values(),
                                 dtype={
                                     'siret': 'str',
                                     'adresse_code_postal': 'str',
                                     'adresse_numero_voie': 'str',
                                     'directeur_code': 'str',
                                     'president_code': 'str',
                                 },
                                 )

    data_president = data_cci[[c for c in mapping_cci.values() if c[:9] == 'president'] + ['id_cci']]
    data_directeur = data_cci[[c for c in mapping_cci.values() if c[:9] == 'directeur'] + ['id_cci']]
    data_cci = data_cci.drop([c for c in mapping_cci.values() if c[:6] == 'unused'], axis=1)
    data_cci = data_cci.drop([c for c in mapping_cci.values() if c[:9] == 'president'], axis=1)
    data_cci = data_cci.drop([c for c in mapping_cci.values() if c[:9] == 'directeur'], axis=1)
    data_cci['siret'] = data_cci['siret'].apply(lambda x: str(x).replace(' ', ''))
    data_cci = data_cci.fillna('')
    data_cci['telephone'] = data_cci['telephone'].apply(lambda x: str(x).strip())
    data_cci['fax'] = data_cci['fax'].apply(lambda x: str(x).strip())
    data_cci['code'] = data_cci['code'].apply(lambda x: x and int(x))
    data_cci['date_creation'] = data_cci['date_creation'].apply(lambda x: x and x.date())

    # Constuire le dataframe pour les adresses
    data_adresse = data_cci[[c for c in mapping_cci.values() if c[:7] == 'adresse'] + ['id_cci']]
    data_adresse = data_adresse.rename(columns={
        'adresse_code_postal': 'code_postal',
        'adresse_commune': 'commune',
        'adresse_distribution_speciale': 'distribution_speciale',
        'adresse_complement_voie': 'complement',
        'adresse_nom_voie': 'nom_voie',
        'adresse_type_voie': 'type_voie',
        'adresse_indice_repetition': 'indice_repetition',
        'adresse_numero_voie': 'numero_voie',
    })
    # Ajouter le type adresse
    data_adresse['type_adresse'] = 'P'

    # Supprime les données adresse
    data_cci = data_cci.drop([c for c in mapping_cci.values() if c[:7] == 'adresse'], axis=1)

    data_president = data_president.rename(columns={
        'president_nom': 'nom',
        'president_prenom': 'prenom',
        'president_code': 'code',
    })

    data_president = data_president[~data_president.nom.isnull()]
    data_president = data_president[~data_president.prenom.isnull()]
    data_president = data_president[data_president.code != '99']
    data_president = data_president.drop_duplicates(subset=['code'])
    data_president['nom'] = data_president['nom'].apply(lambda x: x.strip())
    data_president['prenom'] = data_president['prenom'].apply(lambda x: x.strip())
    data_president['code'] = data_president['code'].apply(lambda x: x.strip())

    data_directeur = data_directeur.rename(columns={
        'directeur_nom': 'nom',
        'directeur_prenom': 'prenom',
        'directeur_code': 'code',
    })
    data_directeur = data_directeur[~data_directeur.nom.isnull()]
    data_directeur = data_directeur[~data_directeur.prenom.isnull()]
    data_directeur = data_directeur[data_directeur.code != '99']
    data_directeur = data_directeur.drop_duplicates(subset=['code'])
    data_directeur['nom'] = data_directeur['nom'].apply(lambda x: x.strip())
    data_directeur['prenom'] = data_directeur['prenom'].apply(lambda x: x.strip())
    data_directeur['code'] = data_directeur['code'].apply(lambda x: x.strip())

    return {
        "cci": data_cci,
        "adresse": data_adresse,
        "president": data_president,
        "directeur": data_directeur,
    }


def construireDataframeQualite(p_fichier):
    return pandas.read_csv(p_fichier, names=['code', 'libelle'], skiprows=1)


if __name__ == "__main__":
    # df = construireDataframeCCI('referentiels/api/management/fichiers/cci.xls')

    # df = construireDataframeQualite('referentiels/api/management/fichiers/qualite.csv')
    # print(df)
    pass
