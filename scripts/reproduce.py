"""Pruebas -> descarga fijada -> Soria -> nacional. Ejecutar desde raíz del repo."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from elecciones.cli import read_catalog
from elecciones.download import fetch, verified_inputs
from elecciones.pipeline import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='Directorio nuevo; no sobrescribe ejecuciones')
    parser.add_argument('--timeout', type=float, default=30)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        parser.error('--output debe ser un directorio nuevo')
    subprocess.run([sys.executable, '-m', 'pytest', '-q'], check=True)
    output.mkdir(parents=True)
    sources = read_catalog('data/sources/catalog.csv')
    pins = json.loads(Path('data/sources/checksums.json').read_text())
    manifest, raw = output / 'manifest.jsonl', Path('data/raw')
    for source_id, checksum in pins.items():
        record = fetch(sources[source_id], raw, manifest,
                       expected_sha256=checksum, timeout=args.timeout)
        if record['status'] != 'ok':
            raise SystemExit(f'Descarga detenida: {source_id}; consulte {manifest}')
    verified_inputs(manifest, raw)
    province = run('data/sources/catalog.csv', manifest, raw, output / 'soria', '42')
    if province['findings']:
        raise SystemExit('Soria tiene observaciones; revisar antes de ampliar cobertura')
    national = run('data/sources/catalog.csv', manifest, raw, output / 'national')
    print(json.dumps({'status': national['status'], 'findings': national['finding_counts'],
                      'report': str(output / 'national' / 'report.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
