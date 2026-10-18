from io import BytesIO
import json
from hashlib import sha256
from urllib.error import HTTPError, URLError
import pytest
from elecciones.download import fetch, verified_inputs, digest

SOURCE={'id':'synthetic','url':'https://example.invalid/data'}


class Response(BytesIO):
    status=200
    def __init__(self,body=b'original bytes',length=None):
        super().__init__(body);self.headers={'Content-Length':str(len(body) if length is None else length),'Content-Type':'application/octet-stream'}
    def geturl(self):return SOURCE['url']


def test_download_hash_and_mutation_detection(tmp_path):
    manifest=tmp_path/'manifest.jsonl';raw=tmp_path/'raw'
    r=fetch(SOURCE,raw,manifest,opener=lambda *a,**kw:Response())
    assert r['sha256']==sha256(b'original bytes').hexdigest()
    assert r['bytes']==14 and r['http_status']==200 and r['status']=='ok'
    assert verified_inputs(manifest,raw)['synthetic'][1]['sha256']==r['sha256']
    (raw/r['path']).write_bytes(b'altered bytes!')
    with pytest.raises(ValueError,match='Integridad'):verified_inputs(manifest,raw)


def test_retries_and_logs_every_attempt(tmp_path):
    calls=[]
    def opener(*args,**kw):
        calls.append(kw['timeout'])
        if len(calls)==1:raise HTTPError(SOURCE['url'],503,'Unavailable',{},None)
        return Response()
    r=fetch(SOURCE,tmp_path/'raw',tmp_path/'m',opener=opener,sleep=lambda n:None,timeout=3)
    entries=[json.loads(x) for x in (tmp_path/'m').read_text().splitlines()]
    assert calls==[3,3] and r['status']=='ok'
    assert entries[0]['http_status']==503 and entries[0]['sha256'] is None
    assert len(entries)==2


def test_404_not_retried(tmp_path):
    def opener(*a,**kw):raise HTTPError(SOURCE['url'],404,'Missing',{},None)
    r=fetch(SOURCE,tmp_path/'raw',tmp_path/'m',opener=opener)
    assert r['attempt']==1 and r['http_status']==404 and r['status']=='failed'


@pytest.mark.parametrize('body,length',[(b'abc',10),(b'',0)])
def test_no_success_for_truncated_or_empty_response(tmp_path,body,length):
    r=fetch(SOURCE,tmp_path/'raw',tmp_path/'m',opener=lambda *a,**kw:Response(body,length))
    assert r['status']=='failed' and r['path'] is None
    assert not list((tmp_path/'raw').iterdir())


def test_hash_mismatch_preserves_original_and_rejects_as_input(tmp_path):
    r=fetch(SOURCE,tmp_path/'raw',tmp_path/'m',expected_sha256='0'*64,opener=lambda *a,**kw:Response())
    assert r['status']=='hash_mismatch'
    assert digest(tmp_path/'raw'/r['path'])==r['sha256']
    with pytest.raises(ValueError,match='sin descargas'):verified_inputs(tmp_path/'m',tmp_path/'raw')


def test_source_never_overwritten(tmp_path):
    one=fetch(SOURCE,tmp_path/'raw',tmp_path/'m',opener=lambda *a,**kw:Response(b'one'))
    two=fetch(SOURCE,tmp_path/'raw',tmp_path/'m',opener=lambda *a,**kw:Response(b'two'))
    assert one['path']!=two['path'] and len(list((tmp_path/'raw').iterdir()))==2


def test_timeout_and_max_size(tmp_path):
    def opener(*a,**kw):raise TimeoutError('synthetic timeout')
    r=fetch(SOURCE,tmp_path/'raw',tmp_path/'m',opener=opener,attempts=2,sleep=lambda n:None)
    assert r['attempt']==2 and r['status']=='failed' and r['sha256'] is None
    r=fetch(SOURCE,tmp_path/'raw',tmp_path/'m',opener=lambda *a,**kw:Response(),max_bytes=2)
    assert r['status']=='failed' and r['path'] is None


def test_invalid_parameters(tmp_path):
    for kw in [dict(attempts=0),dict(attempts=6),dict(timeout=0),dict(expected_sha256='abc')]:
        with pytest.raises(ValueError):fetch(SOURCE,tmp_path/'raw',tmp_path/'m',**kw)


def test_interrupted_stream_is_logged_and_retried(tmp_path):
    from http.client import IncompleteRead
    class Broken(Response):
        def read(self,*args):raise IncompleteRead(b'partial',100)
    r=fetch(SOURCE,tmp_path/'raw',tmp_path/'m',opener=lambda *a,**kw:Broken(),attempts=2,sleep=lambda n:None)
    assert r['status']=='failed' and r['attempt']==2
    assert len((tmp_path/'m').read_text().splitlines())==2
    assert not list((tmp_path/'raw').iterdir())
