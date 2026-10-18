"""Reglas sobre unidades comparables. Hallazgos técnicos, sin causalidad política."""
from collections import Counter
import re

KEY = ('election_date', 'election_type', 'scrutiny_type', 'geography_level',
       'province_code', 'municipality_code', 'district_code', 'section_code',
       'table_code', 'population_scope', 'constituency_code')
TOTAL_FIELDS = ('electors', 'voters', 'valid_votes', 'blank_votes', 'null_votes', 'candidacy_ballots')


def key(row):
    return tuple(row.get(field) for field in KEY)


def finding(rule, observed=None, expected=None, **kwargs):
    return dict(rule=rule, observed=observed, expected=expected,
                status='detected', severity='technical_review', reviewer=None, **kwargs)


def senate_max_marks(province, constituency=None):
    # Art. 96.3 LOREG: límites de selección, no inferencia de nulidad concreta.
    if province in {'51', '52'}:
        return 2
    if province in {'07', '35', '38'}:
        from .dat import INSULAR_DISTRICTS
        if constituency not in INSULAR_DISTRICTS[province]:
            raise ValueError('Límite de marcas requiere circunscripción insular conocida')
        return 2 if (province, constituency) in {('07', '1'), ('35', '1'), ('38', '4')} else 1
    return 3


def validate(totals, results):
    findings = []
    result_sums = Counter()
    parents = {key(r): r for r in totals}
    for kind, rows, fields in [('totals', totals, ()), ('results', results, ('candidacy_key', 'candidate_code'))]:
        counts = Counter()
        for r in rows:
            counts[key(r) + tuple(r.get(f) for f in fields)] += 1
            if kind == 'results' and type(r.get('votes')) is int and r['votes'] >= 0:
                result_sums[key(r)] += r['votes']
            context = dict(entity=kind, geography_key=list(key(r)), source_id=r['source_id'], source_locators=r.get('source_locators', []))
            if kind == 'results':
                parent = parents.get(key(r))
                if parent is None:
                    findings.append(finding('orphan_result', **context))
                elif r['election_type'] == 'senate' and type(r.get('votes')) is int and type(parent.get('candidacy_ballots')) is int and r['votes'] > parent['candidacy_ballots']:
                    findings.append(finding('candidate_votes_exceed_ballots', r['votes'], parent['candidacy_ballots'], **context))
            for field in (TOTAL_FIELDS if kind == 'totals' else ('votes',)):
                value = r.get(field)
                if value is None or type(value) is not int or value < 0:
                    findings.append(finding('invalid_count', value, 'nonnegative integer', field=field, **context))
            widths = {'province_code': 2, 'municipality_code': 3, 'district_code': 2, 'section_code': 4}
            for field, width in widths.items():
                v = r.get(field)
                required = field == 'province_code' or r.get('geography_level') == 'table'
                if (required and v is None) or (v is not None and not re.fullmatch(r'\d{3}[ A-Z0-9]' if field == 'section_code' else r'\d{' + str(width) + '}', v)):
                    findings.append(finding('invalid_geography_code', v, f'{width} digits', field=field, **context))
            if r.get('geography_level') == 'table' and not r.get('table_code'):
                findings.append(finding('missing_table_code', **context))
        findings += [finding('duplicate_key', n, 1, entity=kind, geography_key=list(k))
                     for k, n in counts.items() if n > 1]
    for r in totals:
        context = dict(geography_key=list(key(r)), source_id=r['source_id'], source_locators=r.get('source_locators', []))
        if all(type(r.get(f)) is int and r[f] >= 0 for f in TOTAL_FIELDS):
            for rule, actual, expected in [
                ('valid_plus_null', r['valid_votes'] + r['null_votes'], r['voters']),
                ('candidacy_plus_blank', r['candidacy_ballots'] + r['blank_votes'], r['valid_votes']),
            ]:
                if not r.get('derived_counts') and actual != expected:
                    findings.append(finding(rule, actual, expected, **context))
            if r['voters'] > r['electors']:
                findings.append(finding('voters_exceed_electors', r['voters'], r['electors'], **context))
            if r['election_type'] == 'senate':
                maximum = senate_max_marks(r['province_code'], r.get('constituency_code'))
                capacity = maximum * r['candidacy_ballots']
                if result_sums[key(r)] > capacity:
                    findings.append(finding('senate_marks_exceed_capacity', result_sums[key(r)], capacity, max_marks=maximum, ballots=r['candidacy_ballots'], legal_reference='LOREG art. 96.3', **context))
            # Senado: marcas por candidato no son papeletas. No sumar como Congreso.

            if r['election_type'] == 'congress' and result_sums[key(r)] != r['candidacy_ballots']:
                findings.append(finding('candidacy_sum', result_sums[key(r)], r['candidacy_ballots'], **context))
    return findings


def compare_totals(derived, published):
    """Sin cruces automáticos entre ámbitos, censos, elecciones o escrutinios."""
    if key(derived) != key(published) or derived['scrutiny_type'] == 'unknown':
        raise ValueError('Magnitudes no comparables o escrutinio desconocido')
    return [finding('published_total_mismatch', derived[f], published[f], field=f,
                    source_ids=[derived['source_id'], published['source_id']])
            for f in TOTAL_FIELDS if derived[f] != published[f]]


def coverage(observed, expected=None, denominator=None):
    """Un listado de IDs permite identificar faltantes; un total solo contarlos."""
    observed = set(observed)
    if expected is not None:
        expected = set(expected)
        return dict(observed=len(observed), denominator=len(expected),
                    covered=len(observed & expected), missing=len(expected - observed),
                    missing_keys=sorted(expected - observed), unexpected_keys=sorted(observed - expected),
                    ratio=len(observed & expected) / len(expected) if expected else None)
    return dict(observed=len(observed), denominator=denominator,
                covered=len(observed), missing=None if denominator is None else max(0, denominator - len(observed)),
                missing_keys=None, unexpected_keys=None,
                ratio=len(observed) / denominator if denominator else None)
