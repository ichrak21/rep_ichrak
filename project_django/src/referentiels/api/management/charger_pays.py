from collections import OrderedDict
import sys
import pandas
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import types, MetaData, Table
from sqlalchemy.schema import CreateSchema
from sqlalchemy.orm import sessionmaker

try:
    import utils, config
except ImportError:
    from referentiels.api.management import utils, config

# Fichiers source
# TODO : les obtenirs depuis une source externe
CSV_INSEE = config.FICHIERS['pays_insee']
CSV_CFENET = config.FICHIERS['pays_cfenet']
XLS_CONTINENT = config.FICHIERS['continents']

# Entêtes fichiers INSEE et nom en base
mapping_insee = OrderedDict({
    'COG': 'code_officiel_geo',
    'ACTUAL': 'code_actualite',
    'CAPAY': 'code_ancien_pays',
    'CRPAY': 'code_pays_ratt',
    'ANI': 'annee_inde',
    'LIBCOG': 'libelle',
    'LIBENR': 'libelle_complet',
    'ANCNOM': 'ancien_nom',
    'CODEISO2': 'codeiso2',
    'CODEISO3': 'codeiso3',
    'CODENUM3': 'code_num3',
    'CODECONTINENT': 'continent',
})
# Entêtes fichiers CFENet et nom en base
mapping_cfenet = OrderedDict({
    'code': 'codecfe',
    'libelle': 'unused_libellecfe',
    'est_ue': 'estue',
    'est_eee': 'esteee',
    'libelle_nationalite': 'nationalite',
    'code_iso_an_2': 'unused_code_iso_an_2',
    'code_iso_an_3': 'codeiso3',
    'code_iso_n': 'unused_code_iso_n'
})


def construireDataframePays(p_fichierInsee, p_fichierCfe):
    # Lecture du CSV INSEE des pays
    data_insee = pandas.read_csv(p_fichierInsee, sep="\t", encoding='latin-1', names=mapping_insee.values(), skiprows=1,
                                 dtype={
                                     'code_ancien_pays': 'str',
                                     'code_officiel_geo': 'str',
                                     'code_pays_ratt': 'str',
                                     'codeiso3': 'str',
                                 })

    # Lecture du CSV CFENET des pays
    data_cfenet = pandas.read_csv(p_fichierCfe, sep=",", encoding="utf8", names=mapping_cfenet.values(), skiprows=1,
                                  dtype={'codecfe': 'str', 'codeiso3': 'str'})
    # Convertir en boolean les colonnes concernees
    data_cfenet['estue'] = data_cfenet['estue'].apply(lambda x: x == 't')
    data_cfenet['esteee'] = data_cfenet['esteee'].apply(lambda x: x == 't')

    data_cfenet = data_cfenet.set_index('codeiso3')
    # Nettyoage des lignes sans index i.e. sans codeiso3
    data_cfenet = data_cfenet.dropna(axis=0)

    # Fusion des fichiers sur la colonne codeiso3
    data_pays = data_cfenet.merge(data_insee, on='codeiso3')
    # Suppression des colonnes en doublon marqué par le prefixe unused_
    data_pays = data_pays.drop(['unused_code_iso_an_2', 'unused_code_iso_n', 'unused_libellecfe'], axis=1)
    # Ajout de la colonne actif
    data_pays['actif'] = True

    # Remplir les cases vides avec une chaine vide ''
    data_pays.ancien_nom = data_pays.ancien_nom.fillna('')
    data_pays.code_ancien_pays = data_pays.code_ancien_pays.fillna('')
    data_pays.code_pays_ratt = data_pays.code_pays_ratt.fillna('')

    return data_pays


def construireDataframeContinent(p_fichier):
    # Obtenir les continents
    data_continents = pandas.read_excel(p_fichier, na_filter=False)
    return data_continents


def initialisationEnBase(p_dataPays, p_dataContinent, p_delete=True):
    # Mise à jour en base de données
    engine = create_engine(config.DB_ENGINE)
    session = sessionmaker(bind=engine)()
    # try:
    #    engine.execute(CreateSchema('refv2'))
    # except sqlalchemy.exc.ProgrammingError:
    #    pass
    Pays = Table("api_pays", MetaData(engine), autoload=True)
    Continent = Table("api_continent", MetaData(engine), autoload=True)
    if p_delete:
        # Vider les tables
        try:  # Pays
            session.execute(Pays.delete())
            session.commit()
        except sqlalchemy.exc.NoSuchTableError:
            pass

        try:  # Continents
            session.execute(Continent.delete())
            session.commit()
        except sqlalchemy.exc.NoSuchTableError:
            pass
        session.close()

    # Enregistrement des continents en base de données
    p_dataContinent.to_sql('api_continent',
                           engine,
                           if_exists='append',
                           index=False,
                           dtype={
                               'actif': types.Boolean(),
                               'code': types.String(2),
                               'libelle': types.String(100)
                           }
                           )
    # Jointure entre les pays et les continents
    q = session.query(Continent)
    continentsByCode = utils.sort_by_key_to_dict('code', q.all(), Continent)
    p_dataPays['continent_id'] = p_dataPays['continent'].apply(
        lambda x: continentsByCode.get(x) and continentsByCode.get(x)['id'])

    # Suppression de la colonne continent 
    p_dataPays = p_dataPays.drop(['continent'], axis=1)

    # Enregistrement des pays en base de données
    p_dataPays.to_sql('api_pays',
                      engine,
                      if_exists='append',
                      index=False,
                      # index_label='id',
                      dtype={
                          'code_ancien_pays': types.String(5),
                          'ancien_nom': types.String(100),
                          'annee_inde': types.Integer(),
                          'codecfe': types.String(5),
                          'codeiso2': types.String(2),
                          'codeiso3': types.String(3),
                          'code_num3': types.Integer(),
                          'code_officiel_geo': types.String(5),
                          'code_pays_ratt': types.String(5),
                          'esteee': types.Boolean(),
                          'estue': types.Boolean(),
                          'libelle': types.String(100),
                          'libelle_complet': types.String(100),
                          'nationalite': types.String(100),
                          'code_actualite': types.Integer(),
                          'continent': types.String(2),
                      }
                      )
