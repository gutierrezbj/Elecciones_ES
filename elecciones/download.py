"""Descarga por streaming, originales inmutables y manifest JSONL por intento."""
from datetime import datetime, timezone
from hashlib import sha256
from http.client import IncompleteRead
import json
import logging
from pathlib import Path
import re
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

LOG = logging.getLogger(__name__)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def append_manifest(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n')


def fetch(source, raw_dir, manifest, *, timeout=20, attempts=3,
          expected_sha256=None, max_bytes=256 * 1024 * 1024, opener=urlopen,
          sleep=time.sleep):
    """No cache silenciosa: cada invocación registra cada intento HTTP.

    timeout limita cada operación de socket y la duración total del streaming.
    El hash esperado es opcional y su procedencia la fija quien invoca la CLI.
    """
    if not re.fullmatch(r'[a-z0-9_-]+', source['id']):
        raise ValueError('source_id inválido')
    if urlparse(source['url']).scheme not in {'https', 'http'}:
        raise ValueError('Solo se admiten URLs HTTP(S)')
    if timeout <= 0 or not 1 <= attempts <= 5 or max_bytes <= 0:
        raise ValueError('timeout/max_bytes positivos; attempts entre 1 y 5')
    if expected_sha256 and not re.fullmatch('[0-9a-f]{64}', expected_sha256):
        raise ValueError('SHA-256 esperado inválido')
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, attempts + 1):
        record = dict(source_id=source['id'], url=source['url'], retrieved_at=now(),
                      attempt=attempt, http_status=None, bytes=0, sha256=None,
                      path=None, status='failed', error=None, final_url=None,
                      expected_sha256=expected_sha256)
        temporary = None
        retry = False
        started = time.monotonic()
        try:
            request = Request(source['url'], headers={'User-Agent': 'Elecciones_ES/0.1 (source verification)'})
            with opener(request, timeout=timeout) as response:
                record.update(http_status=response.status, final_url=response.geturl(),
                              content_type=response.headers.get('Content-Type'),
                              etag=response.headers.get('ETag'),
                              last_modified=response.headers.get('Last-Modified'))
                if response.status != 200:
                    raise ValueError(f'HTTP inesperado: {response.status}')
                h = sha256()
                with tempfile.NamedTemporaryFile(dir=raw_dir, delete=False) as stream:
                    temporary = Path(stream.name)
                    while chunk := response.read(1024 * 1024):
                        record['bytes'] += len(chunk)
                        if record['bytes'] > max_bytes:
                            raise ValueError('Límite de tamaño superado')
                        if time.monotonic() - started > timeout:
                            raise TimeoutError('Tiempo total de descarga agotado')
                        stream.write(chunk)
                        h.update(chunk)
                size = response.headers.get('Content-Length')
                if size is not None and int(size) != record['bytes']:
                    raise ValueError('Content-Length no coincide; descarga truncada')
                if not record['bytes']:
                    raise ValueError('Respuesta vacía')
                record['sha256'] = h.hexdigest()
                # Nombre independiente del nombre remoto y de los redirects.
                target = raw_dir / f"{source['id']}-{h.hexdigest()}.raw"
                if target.exists():
                    if digest(target) != h.hexdigest():
                        raise ValueError('Original local alterado; no se sobrescribe')
                    temporary.unlink()
                else:
                    temporary.rename(target)
                temporary = None
                record['path'] = target.name
                if expected_sha256 and h.hexdigest() != expected_sha256:
                    record['status'] = 'hash_mismatch'
                    record['error'] = 'El original se conserva; no coincide con el hash esperado'
                else:
                    record['status'] = 'ok'
        except HTTPError as exc:
            record.update(http_status=exc.code, error=f'HTTP {exc.code}')
            retry = exc.code in {408, 429} or 500 <= exc.code <= 599
        except (URLError, TimeoutError, ConnectionError, OSError, IncompleteRead) as exc:
            record['error'] = f'{type(exc).__name__}: {exc}'
            retry = True
        except ValueError as exc:
            record['error'] = str(exc)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        append_manifest(manifest, record)
        LOG.info(json.dumps({k: record[k] for k in ('source_id', 'attempt', 'status', 'http_status', 'error')}, ensure_ascii=False))
        if record['status'] != 'failed' or not retry or attempt == attempts:
            return record
        sleep(min(2 ** (attempt - 1), 8))
    raise AssertionError('unreachable')


def verified_inputs(manifest, raw_dir):
    """Verifica TODOS los éxitos del manifest; devuelve el último por fuente.

    Un fallo posterior no borra un éxito histórico. Nunca usa hash_mismatch.
    """
    selected = {}
    raw_dir = Path(raw_dir).resolve()
    for line in Path(manifest).read_text(encoding='utf-8').splitlines():
        r = json.loads(line)
        if r['status'] != 'ok':
            continue
        path = (raw_dir / r['path']).resolve()
        if path.parent != raw_dir:
            raise ValueError('Ruta fuera de raw_dir')
        if not path.is_file() or path.stat().st_size != r['bytes'] or digest(path) != r['sha256']:
            raise ValueError(f"Integridad fallida: {r['source_id']}")
        selected[r['source_id']] = (path, r)
    if not selected:
        raise ValueError('Manifest sin descargas verificables')
    return selected
