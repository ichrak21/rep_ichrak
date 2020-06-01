def row_to_dict(row, table):
    """ Convertir une ligne (tuple en dictionnnaire) 
    @param row: tuple par exemple (56, 'Pizza', '4 fromages')
    @param table: sqlalchemy.sql.schema.Table
    @return dictinnaire {table.colnum: valeur} par exemple {'id': 56, 'categorie': 'Pizza', 'type': '4 fromages'}
    """
    return dict((column.name, getattr(row, column.name)) for column in table.columns)


def sort_by_key_to_dict(key, fetchAll, table):
    """ Convertir l'ensemble d'un fetch all en dictionnaire sur la colonne key, par exemple
    ```
        sort_by_key_to_dict('categorie', [(56, 'Pizza', '4 fromages'), ...], Menu)
        {'Pizza': {'id': 56, 'categorie': 'Pizza', 'type': '4 fromages'}}
        sort_by_key_to_dict('id', [(56, 'Pizza', '4 fromages'), ...], Menu)
        {'56': {'id': 56, 'categorie': 'Pizza', 'type': '4 fromages'}}
    ```
    @param key: cle entrée du dictionnaire
    @param fetchAll: liste de tuple
    @param table: sqlalchemy.sql.schema.Table
    @return dictinnaire cf. exemple
    """
    result = {}
    for row in fetchAll:
        d = row_to_dict(row, table)
        result[d[key]] = d
    return result
