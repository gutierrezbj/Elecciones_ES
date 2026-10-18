"""Denominadores oficiales INE; no equivalen a resultados electorales."""
from collections import defaultdict
import csv
import re


def read_denominators(path):
    with open(path, encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, delimiter=';')
        if reader.fieldnames != ['Provincias', 'Número', 'Total']:
            raise ValueError('Cabecera INE 59781 no reconocida')
        result = defaultdict(dict)
        for line, row in enumerate(reader, 2):
            if row['Número'] not in {'Municipios', 'Mesas electorales'}:
                continue
            name, kind = row['Provincias'], row['Número']
            if kind in result[name]:
                raise ValueError('Denominador duplicado')
            value = row['Total'].replace('.', '')
            if not re.fullmatch(r'\d+', value):
                raise ValueError('Denominador no numérico')
            result[name][kind] = dict(value=int(value), source_locator=f'line:{line}')
        if 'TOTAL' not in result:
            raise ValueError('Falta el total nacional INE')
        for kind in ('Municipios', 'Mesas electorales'):
            if sum(v[kind]['value'] for k, v in result.items() if k != 'TOTAL') != result['TOTAL'][kind]['value']:
                raise ValueError('Denominadores provinciales INE no suman el total nacional')
        return dict(result)
