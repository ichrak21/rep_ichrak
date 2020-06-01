#!/usr/bin/env python3
"""
Prépare les fichiers pour le chargement en base de données via l'ORM de Django
"""
from collections import OrderedDict
import pandas
import datetime

mapping_cfe = OrderedDict({
    'CH_COD': 'code',
    'CH_NOM': 'libelle',
    'CH_QUA': 'unused_1',
    'CH_LIE': 'unused_2',
    'LIBELLES COURTS': 'libelle_court',
    'CH_CDX': 'unused_60',
    'CH_COM': 'adresse_code_commune',
    'CH_CPL': 'adresse_complement',
    'CH_NUM': 'adresse_numero_voie',
    'CH_POS': 'adresse_code_postal',
    'CH_REP': 'adresse_indice_repetition',
    'CH_RIV': 'unused_3',
    'CH_SPE': 'adresse_distribution_speciale',
    'CH_DIS0': 'unused_4',
    'CH_TYP': 'adresse_type_voie',
    'CH_VOI': 'adresse_nom_voie',
    'CH_PAY': 'unused_5',
    'CH_DIS1': 'unused_6',
    'CH_DIS2': 'unused_7',
    'CH_DIS3': 'unused_8',
    'CH_DIS4': 'unused_9',
    'CH_DIS5': 'unused_10',
    'CH_DIS6': 'unused_11',
    'CH_DIS7': 'unused_12',
    'CH_DIS8': 'unused_13',
    'CH_DIS9': 'unused_14',
    'CH_DISA': 'unused_15',
    'CH_DISB': 'unused_16',
    'CH_DISC': 'unused_17',
    'CH_DISD': 'unused_18',
    'CH_DISE': 'unused_19',
    'CH_DISF': 'unused_20',
    'CH_DISG': 'unused_21',
    'CH_DISH': 'unused_22',
    'CH_DISI': 'unused_23',
    'CH_DISJ': 'unused_24',
    'CH_DISK': 'unused_25',
    'CH_DISL': 'unused_26',
    'CH_DISM': 'unused_27',
    'CH_DISN': 'unused_28',
    'CH_DISO': 'unused_29',
    'CH_DISP': 'unused_30',
    'CH_DISQ': 'unused_31',
    'CH_DISR': 'unused_32',
    'CH_DISS': 'unused_33',
    'CH_DIST': 'unused_34',
    'CH_DISU': 'unused_35',
    'CH_DISV': 'unused_36',
    'CH_DISW': 'unused_37',
    'CH_DISX': 'unused_38',
    'CH_DISY': 'unused_39',
    'CH_DISZ': 'unused_40',
    'CH_DIS_': 'unused_41',
    'CH_TEL': 'telephone',
    'CH_FAX': 'fax',
    'CH_MODEM': 'unused_42',
    'CH_APP_LOT': 'unused_43',
    'CH_ENR_ANN': 'unused_44',
    'CH_ENR_NUM': 'unused_45',
    'CH_CPT_BRO': 'unused_46',
    'CH_PRE_LIA': 'unused_47',
    'CH_CONNEX': 'unused_48',
    'CH_MODEM2': 'unused_49',
    'CH_ATT': 'unused_50',
    'CH_IND': 'unused_51',
    'CH_OBS': 'unused_52',
    'CH_UTIL': 'unused_53',
    'CH_PSU': 'unused_54',
    'CH_PSR': 'unused_55',
    'CH_DEV': 'unused_56',
    'CH_LIA_PRE': 'unused_57',
    'CH_VERSION': 'unused_58',
    'CH_VIL': 'unused_59',
    'CH_MAIL': 'courriel',
    'CH_URL': 'url_site_web',
})


def construireDataframeCFE(p_fichier):
    """
    Construit deux dataframe à partir du fichier p_fichier des CFE
    l'un pour les données du CFE l'autre pour l'adresse
    Retourne ces deux dataframes dans via un dictionnaire :
    {
        'cfe': pandas.Dataframe,
        'adresse': pandas.Dataframe
    }
    """

    data_cfe = pandas.read_excel(p_fichier, names=mapping_cfe.values(),
                                 usecols='A:BW',
                                 dtype={
                                     'code': 'str',
                                     'libelle': 'str',
                                     'libelle_court': 'str',
                                     'adresse_numero_voie': 'str',
                                     'telephone': 'str',
                                     'fax': 'str',
                                     'adresse_cedex': 'str',
                                     'adresse_code_postal': 'str',
                                     'adresse_code_commune': 'str',
                                     'courriel': 'str',
                                     'url_site_web': 'str',
                                 })
    # Suppression des colonnes inutiles
    data_cfe = data_cfe.drop([c for c in mapping_cfe.values() if c[:6] == 'unused'], axis=1)
    # Suppression des lignes sans code CFE
    data_cfe = data_cfe[~data_cfe['code'].isnull()]
    # Remplir les null avec une chaine vide
    data_cfe = data_cfe.fillna('')
    # Supprimer les espaces
    data_cfe['telephone'] = data_cfe['telephone'].apply(lambda x: x and x.replace(' ', ''))
    data_cfe['fax'] = data_cfe['fax'].apply(lambda x: x and x.replace(' ', ''))
    data_cfe['courriel'] = data_cfe['courriel'].apply(lambda x: x and x.replace(' ', ''))
    data_cfe['url_site_web'] = data_cfe['url_site_web'].apply(lambda x: x and x.replace(' ', ''))
    # Ajout de http:// si non présent
    data_cfe['url_site_web'] = data_cfe['url_site_web'].apply(lambda x: x and x[:4] != 'http' and 'http://' + x or x)

    # Construire le dataframe adresse ajout du code pour la jointure
    data_adresse = data_cfe[[c for c in mapping_cfe.values() if c[:7] == 'adresse'] + ['code']]
    # Normaliser les noms
    data_adresse = data_adresse.rename(columns={
        'adresse_code_commune': 'code_commune',
        'adresse_complement': 'complement',
        'adresse_numero_voie': 'numero_voie',
        'adresse_code_postal': 'code_postal',
        'adresse_indice_repetition': 'indice_repetition',
        'adresse_distribution_speciale': 'distribution_speciale',
        'adresse_type_voie': 'type_voie',
        'adresse_nom_voie': 'nom_voie',
    })
    # Supprimer les espaces
    data_adresse['nom_voie'] = data_adresse['nom_voie'].apply(lambda x: x and x.strip())
    data_adresse['type_voie'] = data_adresse['type_voie'].apply(lambda x: x and x.strip())
    data_adresse['distribution_speciale'] = data_adresse['distribution_speciale'].apply(lambda x: x and x.strip())
    # Ajouter le type adresse
    data_adresse['type_adresse'] = 'P'

    # Supprime les données adresse du dataframe CFE
    data_cfe = data_cfe.drop([c for c in mapping_cfe.values() if c[:7] == 'adresse'], axis=1)
    return {'cfe': data_cfe, 'adresse': data_adresse}


if __name__ == '__main__':
    # df = construireDataframeCFE('./referentiels/api/management/fichiers/cfe.xls')
    # print(df)
    pass
