"""Anchos definidos en FICHEROS.doc del propio ZIP: secciones 02, 07, 09, 10.

No se abre el fichero 04 de nombres de candidatos. No se extrae el ZIP a disco.
"""
import re
from zipfile import ZipFile


def integer(line, start, end):
    raw = line[start - 1:end]
    if not raw.isascii() or not raw.isdigit():
        raise ValueError(f'Campo numérico inválido en posiciones {start}..{end}')
    return int(raw)


def records(archive, name, width, prefix):
    with archive.open(name) as stream:
        for number, raw in enumerate(stream, 1):
            line = raw.rstrip(b'\r\n').decode('latin1')
            if len(line) != width or not line.startswith(prefix):
                raise ValueError(f'{name}:{number}: ancho/proceso inesperado')
            yield number, line


def common(line, source, locator, level, scope):
    return dict(election_date='2023-07-23', election_type=source['election_type'],
                scrutiny_type='definitive' if line[-1] == 'S' else 'unknown',
                geography_level=level, province_code=line[11:13],
                municipality_code=line[13:16] if level in {'table', 'cera'} else None,
                district_code=line[16:18] if level in {'table', 'cera'} else None,
                section_code=line[18:22] if level in {'table', 'cera'} else None,
                table_code=line[22:23] if level in {'table', 'cera'} else None,
                population_scope=scope, source_id=source['id'], source_locators=[locator])


INSULAR_DISTRICTS = {'07': {'1', '2', '3'}, '35': {'1', '2', '3'}, '38': {'4', '5', '6', '7'}}


def retain_cera(line, chamber):
    p, district = line[11:13], line[16:18]
    if chamber == 'senate' and p in INSULAR_DISTRICTS:
        return district != '09'
    return district == '09'


def read_dat(path, source, province=None):
    code = {'congress': '02', 'senate': '03'}[source['election_type']]
    prefix, suffix = code + '2023071', code + '2307.DAT'
    totals, published, notes = [], [], []
    with ZipFile(path) as archive:
        names = archive.namelist()
        required = ['02' + suffix, '07' + suffix, '09' + suffix, '10' + suffix, 'FICHEROS.doc']
        if any(names.count(n) != 1 for n in required):
            raise ValueError('ZIP incompleto o miembros duplicados')
        identification = list(records(archive, '02' + suffix, 40, prefix))
        if len(identification) != 1 or identification[0][1][12:20] != '23072023':
            raise ValueError('Fecha electoral distinta del 23J')
        municipality_constituencies = {}
        if source['election_type'] == 'senate' and (province is None or province in INSULAR_DISTRICTS):
            name = '05' + suffix
            if names.count(name) != 1:
                raise ValueError('Se requiere 05 para asignar municipios insulares a circunscripción')
            for n, line in records(archive, name, 233, prefix):
                if line[11:13] not in INSULAR_DISTRICTS or line[16:18] != '99':
                    continue
                district = line[118]
                if district not in INSULAR_DISTRICTS[line[11:13]]:
                    raise ValueError('Distrito electoral insular inválido en 05')
                geo = (line[11:13], line[13:16])
                if geo in municipality_constituencies:
                    raise ValueError('Municipio insular duplicado en 05')
                municipality_constituencies[geo] = district
        # Preservar también el nivel de circunscripción insular del Senado.
        for n, line in records(archive, '07' + suffix, 172, prefix):
            p = line[11:13]
            if p == '99' or (province and p != province):
                continue
            if line[13] != '9' and not (source['election_type'] == 'senate' and line[13] in INSULAR_DISTRICTS.get(p, set())):
                continue
            if line[-1] not in 'SN':
                raise ValueError('Indicador oficial inválido')
            row = common(line, source, f'07{suffix}:line:{n}', 'province' if line[13] == '9' else 'constituency', 'total')
            row['constituency_code'] = line[13]
            blank, null, candidacy = (integer(line, a, b) for a, b in [(126, 133), (134, 141), (142, 149)])
            row.update(province_name=line[14:64].strip(), electors=integer(line, 86, 93),
                electors_ine=integer(line, 78, 85), published_tables=integer(line, 73, 77),
                blank_votes=blank, null_votes=null, candidacy_ballots=candidacy,
                valid_votes=blank + candidacy, voters=blank + candidacy + null, derived_counts='valid_votes,voters')
            published.append(row)
        if not published:
            raise ValueError('No hay provincias publicadas en ámbito solicitado')
        for n, line in records(archive, '09' + suffix, 101, prefix):
            p, m = line[11:13], line[13:16]
            if p == '99' or (province and p != province):
                continue
            # Retener islas del Senado y excluir su rollup provincial; Congreso mantiene 09.
            if m == '999' and not retain_cera(line, source['election_type']):
                notes.append(dict(rule='excluded_cera_rollup', province_code=p,
                                  source_locator=f'09{suffix}:line:{n}', status='explained'))
                continue
            if line[-1] not in 'SN':
                raise ValueError('Indicador oficial inválido')
            row = common(line, source, f'09{suffix}:line:{n}', 'cera' if m == '999' else 'table', 'cera' if m == '999' else 'cer')
            if source['election_type'] == 'senate' and p in INSULAR_DISTRICTS:
                if m == '999':
                    district = str(int(line[16:18]))
                else:
                    district = municipality_constituencies.get((p, m))
                if district not in INSULAR_DISTRICTS[p]:
                    raise ValueError('No se puede asignar circunscripción insular desde 05/09')
                row['constituency_code'] = district
            else:
                row['constituency_code'] = '9'
            blank, null, candidacy = (integer(line, a, b) for a, b in [(66, 72), (73, 79), (80, 86)])
            row.update(electors=integer(line, 31, 37), electors_ine=integer(line, 24, 30),
                       blank_votes=blank, null_votes=null, candidacy_ballots=candidacy,
                       valid_votes=blank + candidacy, voters=blank + candidacy + null,
                       official_flag=line[-1], derived_counts='valid_votes,voters')
            totals.append(row)
    return totals, read_results(path, source, totals, province), published, notes


def read_results(path, source, totals, province=None):
    code = {'congress': '02', 'senate': '03'}[source['election_type']]
    prefix, suffix = code + '2023071', code + '2307.DAT'
    # No hay indicador oficial en 10: heredar del registro 09 exacto.
    by_geography = {}
    for t in totals:
        g = tuple(t[f] for f in ('province_code', 'municipality_code', 'district_code', 'section_code', 'table_code'))
        if g in by_geography:
            raise ValueError(f'Duplicado en 09: {g}')
        by_geography[g] = t
    with ZipFile(path) as archive:
        for n, line in records(archive, '10' + suffix, 36, prefix):
            p, m = line[11:13], line[13:16]
            if p == '99' or (province and p != province) or (m == '999' and not retain_cera(line, source['election_type'])):
                continue
            g = (p, m, line[16:18], line[18:22], line[22])
            parent = by_geography.get(g)
            if parent is None:
                raise ValueError(f'10{suffix}:{n}: candidatura sin registro 09')
            identifier = line[23:29]
            if not re.fullmatch(r'\d{6}', identifier):
                raise ValueError('Código candidatura/candidato inválido')
            base = {k: parent[k] for k in ('election_date', 'election_type', 'scrutiny_type', 'geography_level', 'province_code', 'municipality_code', 'district_code', 'section_code', 'table_code', 'population_scope', 'source_id', 'constituency_code')}
            yield dict(base, candidacy_key=identifier if code == '02' else None,
                candidacy_code=identifier if code == '02' else None,
                candidate_code=identifier if code == '03' else None,
                votes=integer(line, 30, 36), source_locators=[f'10{suffix}:line:{n}'])
