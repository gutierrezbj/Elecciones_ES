import argparse
import csv
import json
import logging
from zipfile import BadZipFile
from .download import fetch, verified_inputs


def read_catalog(path):
    with open(path, encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    ids = [r['id'] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError('IDs duplicados en catálogo')
    return {r['id']: r for r in rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Ingesta trazable 23J; no infiere fraude')
    parser.add_argument('--catalog', default='data/sources/catalog.csv')
    sub = parser.add_subparsers(dest='command', required=True)
    fetch_parser = sub.add_parser('download')
    fetch_parser.add_argument('source_ids', nargs='+')
    fetch_parser.add_argument('--timeout', type=float, default=20)
    fetch_parser.add_argument('--attempts', type=int, default=3)
    fetch_parser.add_argument('--expected-sha256', help='Solo para una fuente; hash de referencia externo')
    for name in ('download', 'verify', 'pipeline'):
        p = fetch_parser if name == 'download' else sub.add_parser(name)
        p.add_argument('--raw-dir', default='data/raw')
        p.add_argument('--manifest', default='data/downloads/manifest.jsonl')
        if name == 'pipeline':
            p.add_argument('--province', help='Código oficial 01..52; omitir para nacional')
            p.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    try:
        if args.command == 'download':
            sources = read_catalog(args.catalog)
            if args.expected_sha256 and len(args.source_ids) != 1:
                raise ValueError('--expected-sha256 requiere una sola fuente')
            if any(s not in sources for s in args.source_ids):
                raise ValueError('Fuente desconocida en catálogo')
            records = [fetch(sources[s], args.raw_dir, args.manifest,
                             timeout=args.timeout, attempts=args.attempts,
                             expected_sha256=args.expected_sha256) for s in args.source_ids]
            print(json.dumps(records, ensure_ascii=False))
            return 0 if all(r['status'] == 'ok' for r in records) else 1
        if args.command == 'verify':
            selected = verified_inputs(args.manifest, args.raw_dir)
            print(json.dumps({s: r['sha256'] for s, (_, r) in selected.items()}, sort_keys=True))
            return 0
        from .pipeline import run
        report = run(args.catalog, args.manifest, args.raw_dir, args.output, args.province)
        print(json.dumps({k: report[k] for k in ('rows', 'finding_counts')}, ensure_ascii=False))
        return 1 if report['findings'] else 0
    except (ValueError, OSError, KeyError, BadZipFile) as exc:
        logging.error('%s: %s', type(exc).__name__, exc)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
