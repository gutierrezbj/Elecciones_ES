"""Pipeline DAT: una provincia y el mismo adaptador para todo el país."""
from collections import Counter
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import pyarrow as pa
import pyarrow.parquet as pq
from .download import now, verified_inputs, digest
from .dat import read_dat
from .ingest import read_denominators
from .validation import validate, coverage, finding, compare_totals, TOTAL_FIELDS


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def table(rows):
    result = pa.Table.from_pylist(rows)
    numeric = {'votes', 'electors', 'electors_ine', 'published_tables', 'voters', 'valid_votes', 'blank_votes', 'null_votes', 'candidacy_ballots'}
    fields = [pa.field(f.name, pa.int64() if f.name in numeric else pa.list_(pa.string()) if f.name == 'source_locators' else pa.string()) for f in result.schema]
    return result.cast(pa.schema(fields))


def persist_results(rows, path, stats):
    """Produce Parquet por lotes sin materializar millones de resultados."""
    writer, batch = None, []
    try:
        for row in rows:
            stats['results'] += 1
            batch.append(row)
            if len(batch) == 10000:
                chunk = table(batch)
                if writer is None:
                    writer = pq.ParquetWriter(path, chunk.schema, compression='zstd')
                writer.write_table(chunk)
                batch = []
            yield row
        if batch:
            chunk = table(batch)
            if writer is None:
                writer = pq.ParquetWriter(path, chunk.schema, compression='zstd')
            writer.write_table(chunk)
        if writer is None:
            raise ValueError('No hay resultados de candidaturas/candidatos')
    finally:
        if writer:
            writer.close()


def run(catalog, manifest, raw_dir, output, province=None):
    from .cli import read_catalog
    sources = read_catalog(catalog)
    inputs = verified_inputs(manifest, raw_dir)
    required = ['interior_congress_mesa', 'interior_senate_mesa', 'ine_geography_23j']
    if any(s not in inputs for s in required):
        raise ValueError('Se requieren ZIP Congreso/Senado y denominadores INE verificados')
    if province is not None and province not in {str(i).zfill(2) for i in range(1, 53)}:
        raise ValueError('Provincia debe ser código de dos dígitos 01..52')
    out = Path(output)
    if out.exists() and any(out.iterdir()):
        raise ValueError('Directorio de salida no vacío; use otro para preservar trazabilidad')
    denominators = read_denominators(inputs['ine_geography_23j'][0])
    # Crear salidas solo después de verificar todos los hashes y el denominador.
    out.mkdir(parents=True, exist_ok=True)
    findings, coverage_rows, reconciliation, notes, provenance = [], [], [], [], {}
    stats = Counter()
    expected_provinces = [province] if province else [str(i).zfill(2) for i in range(1, 53)]
    try:
        for source_id in required[:2]:
            source = sources[source_id]
            chamber = source['election_type']
            totals, results, published, source_notes = read_dat(inputs[source_id][0], source, province)
            notes.extend(source_notes)
            findings.extend(validate(totals, persist_results(results, out / f'{chamber}-results.parquet', stats)))
            pq.write_table(table(totals), out / f'{chamber}-totals.parquet', compression='zstd')
            pq.write_table(table(published), out / f'{chamber}-published.parquet', compression='zstd')
            stats['totals'] += len(totals)
            stats['published'] += len(published)
            with ZipFile(inputs[source_id][0]) as archive:
                from hashlib import sha256
                provenance[source_id] = {'format_document': 'FICHEROS.doc',
                    'format_document_sha256': sha256(archive.read('FICHEROS.doc')).hexdigest()}
            provincial_counts = Counter(p['province_code'] for p in published)
            if set(provincial_counts) != set(expected_provinces) or any(n != 1 for n in provincial_counts.values()):
                raise ValueError('Cobertura provincial incompleta o duplicada en 07')
            for p in published:
                code = p['province_code']
                physical = [r for r in totals if r['province_code'] == code and r['geography_level'] == 'table']
                cera = [r for r in totals if r['province_code'] == code and r['geography_level'] == 'cera']
                if len(cera) != 1:
                    raise ValueError(f'{chamber} {code}: se requiere un agregado CERA provincial 09')
                # INE y DAT usan las mismas denominaciones salvo acentos/mayúsculas.
                import unicodedata
                def normalized(name):
                    return ''.join(c for c in unicodedata.normalize('NFKD', name.casefold()) if not unicodedata.combining(c)).strip()
                aliases = {'07': 'Balears, Illes', '35': 'Palmas, Las', '15': 'Coruña, A', '26': 'Rioja, La', '03': 'Alicante/Alacant', '12': 'Castellón/Castelló'}
                expected_name = aliases.get(code, p['province_name'])
                matches = [name for name in denominators if normalized(name) == normalized(expected_name)]
                if len(matches) != 1:
                    raise ValueError(f'Provincia sin denominador INE unívoco: {p["province_name"]}')
                expected = denominators[matches[0]]
                table_ids = [':'.join(r[f] for f in ('province_code', 'municipality_code', 'district_code', 'section_code', 'table_code')) for r in physical]
                municipality_ids = [r['province_code'] + r['municipality_code'] for r in physical]
                for level, ids, metric in [('municipality', municipality_ids, 'Municipios'), ('table', table_ids, 'Mesas electorales')]:
                    d = expected[metric]
                    cov = coverage(ids, denominator=d['value'])
                    coverage_rows.append(dict(election_type=chamber, scrutiny_type=p['scrutiny_type'], province_code=code,
                        geography_level=level, **cov, denominator_source_id='ine_geography_23j',
                        denominator_locator=d['source_locator'], limitation='Denominador agregado INE: no permite identificar IDs concretos ausentes; igualdad de cardinalidad no prueba igualdad de conjuntos.'))
                    if cov['observed'] != cov['denominator']:
                        findings.append(finding('coverage_count_mismatch', cov['observed'], cov['denominator'], province_code=code, election_type=chamber, geography_level=level))
                if p['published_tables'] != len(physical):
                    findings.append(finding('published_tables_mismatch', len(physical), p['published_tables'], province_code=code, election_type=chamber))
                if any(r['scrutiny_type'] != p['scrutiny_type'] for r in physical + cera):
                    raise ValueError('Mezcla de escrutinios en agregado provincial')
                derived = dict(p)
                for field in TOTAL_FIELDS:
                    derived[field] = sum(r[field] for r in physical + cera)
                discrepancies = compare_totals(derived, p)
                for f in discrepancies:
                    f.update(province_code=code, election_type=chamber,
                        evidence_ids=[source_id, *p['source_locators']],
                        explanation=None)
                findings.extend(discrepancies)
                reconciliation.append(dict(election_type=chamber, province_code=code,
                    scrutiny_type=p['scrutiny_type'], physical_tables=len(physical), cera_records=len(cera),
                    derived={f: derived[f] for f in TOTAL_FIELDS}, published={f: p[f] for f in TOTAL_FIELDS},
                    published_source_locators=p['source_locators'], discrepancies=len(discrepancies)))
        from hashlib import sha256
        for f in findings:
            f['id'] = 'finding:' + sha256(json.dumps(f, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]
        report = dict(status='completed_with_findings' if findings else 'completed', generated_at=now(), province=province, election_date='2023-07-23',
            transformation_version='interior-dat-v1', catalog_sha256=digest(catalog), manifest_sha256=digest(manifest),
            source_inputs={s: {k: v for k, v in inputs[s][1].items() if k in ('source_id', 'sha256', 'retrieved_at', 'url', 'bytes', 'path')} for s in required},
            format_provenance=provenance, rows=dict(stats), coverage=coverage_rows,
            reconciliation=reconciliation, findings=findings, finding_counts=dict(Counter(f['rule'] for f in findings)),
            excluded_rollups=notes,
            national_denominators={k: denominators['TOTAL'][k] for k in ('Municipios', 'Mesas electorales')},
            limitations=[
                'Denominadores INE por provincia: se contrastan cardinalidades, no listas independientes de IDs de mesas o municipios. CERA excluido de ambos denominadores físicos.',
                '09 no publica votantes ni votos válidos por separado: se derivan de candidaturas, blancos y nulos. Esas identidades son estructurales, no verificaciones independientes.',
                'Datos oficiales S se clasifican definitive según la definición de FICHEROS.doc. No se ha adquirido la instantánea provisional de la noche electoral.',
                'Conciliación solo entre 09 y 07 del mismo ZIP y escrutinio; no equivale a comprobación independiente con actas ni con BOE.',
                'Senado: código de candidato, no partido; marcas no se suman como papeletas. No se leen ni exportan nombres personales del fichero 04.',
                'El ZIP original incluye documentación de candidaturas; se conserva privado fuera de Git sin extraer esos ficheros.',
                'No hay actas de mesa ni transcripciones ni conclusiones sobre voto por correo o fraude.',
                'SHA-256 verifica los bytes recuperados; no es una firma electoral.'
            ])
        if 'boe_2023' in inputs:
            root = ET.parse(inputs['boe_2023'][0]).getroot()
            report['boe_later_references'] = [e.attrib['referencia'] for e in root.findall('.//posterior')]
        try:
            report['code_revision'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
            report['code_dirty'] = bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip())
        except (OSError, subprocess.CalledProcessError):
            report['code_revision'], report['code_dirty'] = None, None
        write_json(out / 'report.json', report)
        write_json(out / 'artifacts.json', {p.name: digest(p) for p in sorted(out.iterdir()) if p.is_file()})
        return report
    except Exception as exc:
        write_json(out / 'FAILED.json', {'status': 'failed', 'error': f'{type(exc).__name__}: {exc}', 'generated_at': now()})
        raise
