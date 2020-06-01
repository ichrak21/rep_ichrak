#!/usr/bin/env python3
"""
# Initialisation de référentiel région, département et commune

Ce script s'occupe de charger les référentiels 
* Région
* Département
* Commune

A partir des fichiers CSV source de l'INSEE. cf. fichiers/README.md

* Le script lit les CSV à l'aide de la librairie pandas. i
* Vide les tables de référentiel. 
* Charge la table Région puis alimente le dataframe département avec
l'id de la région.
* Charge la table Département puis alimente le dataframe commune avec l'id
département.
* Charge la table Commune

"""
from collections import OrderedDict
import pandas
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import types, MetaData, Table
from sqlalchemy.orm import sessionmaker

try:
    import utils, config
except ImportError:
    from referentiels.api.management import utils, config

COMMUNES = config.FICHIERS['communes']
DEPARTEMENTS = config.FICHIERS['departements']
REGIONS = config.FICHIERS['regions']

# Entêtes CSV / Entêtes traitement pour le fichier région
mapping_region_insee = OrderedDict({
    "reg": "code",
    "cheflieu": "unused_cheflieu",
    "tncc": "unused_tncc",
    "ncc": "unused_ncc",
    "nccenr": "unused_nccenr",
    "libelle": "libelle"
})


def construireDataframeRegion(p_fichier):
    # Initialisation du dataframe région
    data_regions = pandas.read_csv(p_fichier, sep=",", encoding='UTF-8', names=mapping_region_insee.values(),
                                   skiprows=1, dtype={'code': 'str'})
    # Suppression des colonnes marquée unused_*
    data_regions = data_regions.drop([c for c in mapping_region_insee.values() if c[:6] == 'unused'], axis=1)
    # Ajout de la colonne actif
    data_regions['actif'] = True
    # Ajout de la colonne code_consulaire
    data_regions['code_consulaire'] = ''
    return data_regions


# Entêtes CSV / Entêtes traitement pour le fichier département
mapping_departement_insee = OrderedDict({
    "dep": "code",
    "reg": "reg",
    "cheflieu": "unused_cheflieu",
    "tncc": "unused_tncc",
    "ncc": "unused_ncc",
    "nccenr": "unused_nccenr",
    "libelle": "libelle"

})


def construireDataframeDepartement(p_fichier):
    # Initialisation du dataframe départements
    data_departements = pandas.read_csv(p_fichier, sep=",", encoding='UTF-8', names=mapping_departement_insee.values(),
                                        skiprows=1)
    # Suppression des colonnes marquée unused_*
    data_departements = data_departements.drop([c for c in mapping_departement_insee.values() if c[:6] == 'unused'],
                                               axis=1)
    # Ajout de la colonne actif
    data_departements['actif'] = True
    return data_departements


# Entêtes CSV / Entêtes traitement pour le fichier commune
mapping_commune_insee = OrderedDict({
    "typecom": "unused_typecom",
    "com": "code",
    "reg": "unused_reg",
    "dep": "dep",
    "arr": "unused_arr",
    "tncc": "tncc",
    "ncc": "libelle",
    "nccenr": "unused_libelle_riche",
    "libelle": "unused_libelle",
    "can": "unused_canton",
    "comparent": "unused_comparent"
})


def construireDataframeCommune(p_fichier):
    # Initialisation du dataframe communes
    data_communes = pandas.read_csv(p_fichier, sep=",", encoding='UTF-8', names=mapping_commune_insee.values(),
                                    skiprows=1, dtype={'code': 'str'})
    # Prendre uniquement type 'COM'
    data_communes = data_communes.loc[data_communes['unused_typecom'] == 'COM']
    # Suppression des colonnes marquée unused_*
    data_communes = data_communes.drop([c for c in mapping_commune_insee.values() if c[:6] == 'unused'], axis=1)
    # Ajout de la colonne actif
    data_communes['actif'] = True
    # Ajout de la colonne article
    articles = {
        0: "",
        1: "",
        2: "LE",
        3: "LA",
        4: "LES",
        5: "L'",
        6: "AUX",
        7: "LAS",
        8: "LOS",
    }
    data_communes['article'] = data_communes['tncc'].apply(lambda x: articles.get(x, ''))
    # Supprimer la clonne tncc
    data_communes = data_communes.drop(['tncc'], axis=1)

    return data_communes


def construireDataframeLaposte(p_fichier):
    """ """
    # Initialisation du dataframe du référentiel postal
    data_laposte = pandas.read_csv(p_fichier, sep=";", encoding='UTF-8',
                                   names=['code_commune', 'unused_nom_commune', 'code_postal', 'libelle'], skiprows=1,
                                   dtype={'code_commune': 'str', 'code_postal': 'str'})
    data_laposte['actif'] = True;
    data_laposte = data_laposte.drop(['unused_nom_commune'], axis=1)
    return data_laposte


def construireDataframeCorrespondanceCommune(p_fichier):
    """
    """
    data_correspondance = pandas.read_csv(p_fichier, sep=';', encoding='latin-1',
                                          names=[
                                              'unused_code_postal', 'code', 'unused_libelle_commune',
                                              'code_cfe', 'unused_libelle_cfe', 'id_cci', 'unused_libelle_cci',
                                              'unused_pointa_id', 'unused_Libelle_pointa'
                                          ], skiprows=1

                                          )
    # Supprimer les colonnes inutiles pour réaliser la correspondance
    data_correspondance = data_correspondance.drop(
        [c for c in list(data_correspondance.columns.values) if c[:6] == 'unused'], axis=1)
    col = [c for c in list(data_correspondance.columns.values) if c[:6] != 'unused']
    # Supprimer les doublons (lié au code postaux)
    data_correspondance = data_correspondance.drop_duplicates()
    data_correspondance = data_correspondance.reindex()
    return data_correspondance


def initialisationEnBase(p_dataRegion, p_dataDepartement, p_dataCommune):
    engine = create_engine(config.DB_ENGINE)
    session = sessionmaker(bind=engine)()

    if p_delete:
        # Vider les tables
        try:  # Commune
            Commune = Table("api_commune", MetaData(engine), autoload=True)
            session.execute(Commune.delete())
            session.commit()
        except sqlalchemy.exc.NoSuchTableError:
            pass

        try:  # Département
            Departement = Table("api_departement", MetaData(engine), autoload=True)
            session.execute(Departement.delete())
            session.commit()
        except sqlalchemy.exc.NoSuchTableError:
            pass

        try:  # Région
            Region = Table("api_region", MetaData(engine), autoload=True)
            session.execute(Region.delete())
            session.commit()
        except sqlalchemy.exc.NoSuchTableError:
            pass

    p_dataRegion.to_sql('api_region',
                        engine,
                        if_exists='append',
                        index=False,
                        dtype={
                            'actif': types.Boolean(),
                            'code': types.String(2),
                            'libelle': types.String(100),
                        })
    # Jointure Région / Département
    q = session.query(Region)
    regionsByCode = utils.sort_by_key_to_dict('code', q.all(), Region)
    p_dataDepartement['region_id'] = p_dataDepartement['reg'].apply(
        lambda x: regionsByCode.get(str(x)) and regionsByCode.get(str(x))['id'])
    # Suppression de la colonne reg
    p_dataDepartement = p_dataDepartement.drop(['reg'], axis=1)

    p_dataDepartement.to_sql('api_departement',
                             engine,
                             if_exists='append',
                             index=False,
                             dtype={
                                 'actif': types.Boolean(),
                                 'code': types.String(3),
                                 'libelle': types.String(100),
                             })
    # Jointure commune / département
    q = session.query(Departement)
    departementsByCode = utils.sort_by_key_to_dict('code', q.all(), Departement)
    p_dataCommune['departement_id'] = p_dataCommune['dep'].apply(
        lambda x: departementsByCode.get(x) and departementsByCode.get(x)['id'])
    # Suppression de la colonne dep
    p_dataCommune = p_dataCommune.drop(['dep'], axis=1)

    p_dataCommune.to_sql('api_commune',
                         engine,
                         if_exists='append',
                         index=False,
                         dtype={
                             'actif': types.Boolean(),
                             'code': types.String(5),
                             'libelle': types.String(100),
                             'article': types.String(10)
                         })


if __name__ == "__main__":
    # construireDataframeLaposte('referentiels/api/management/fichiers/laposte_hexasmal_6.31_12.0.csv') df =
    # construireDataframeCorrespondanceCommune(
    # 'referentiels/api/management/fichiers/correspondance_communes_cfe_cci_avec_com.csv')
    df = construireDataframeCommune('referentiels/api/management/fichiers/commune2019.csv')
    print(df.loc[df.code == '56260'].libelle)
    pass
