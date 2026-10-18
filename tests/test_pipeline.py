import csv
from hashlib import sha256
import json
from pathlib import Path
import pyarrow.parquet as pq
import pytest
from conftest import make_zip
from elecciones.cli import main
from elecciones.pipeline import run


@pytest.fixture
def pipeline_inputs(tmp_path):
    raw=tmp_path/'raw';raw.mkdir()
    records=[]
    for chamber in ['congress','senate']:
        path=make_zip(raw/(chamber+'.zip'),chamber)
        records.append(dict(source_id='interior_'+chamber+'_mesa',status='ok',path=path.name,
            sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,url='https://example.invalid/synthetic',retrieved_at='2026-01-01T00:00:00+00:00'))
    ine=raw/'ine.csv';ine.write_text('Provincias;Número;Total\nTOTAL;Municipios;1\nTOTAL;Mesas electorales;1\nSoria;Municipios;1\nSoria;Mesas electorales;1\n',encoding='utf-8-sig')
    records.append(dict(source_id='ine_geography_23j',status='ok',path=ine.name,sha256=sha256(ine.read_bytes()).hexdigest(),bytes=ine.stat().st_size,url='https://example.invalid/synthetic',retrieved_at='2026-01-01T00:00:00+00:00'))
    manifest=tmp_path/'manifest.jsonl';manifest.write_text(''.join(json.dumps(r)+'\n' for r in records))
    catalog=tmp_path/'catalog.csv'
    with catalog.open('w') as stream:
        w=csv.writer(stream);w.writerow(['id','election_type']);w.writerows([['interior_congress_mesa','congress'],['interior_senate_mesa','senate'],['ine_geography_23j','both']])
    return catalog,manifest,raw


def test_pipeline_preserves_keys_hashes_cera_and_parquet(pipeline_inputs,tmp_path):
    c,m,raw=pipeline_inputs
    r=run(c,m,raw,tmp_path/'out','42')
    assert r['status']=='completed' and r['findings']==[]
    assert r['rows']=={'results':4,'totals':4,'published':2}
    assert all(c['observed']==1 and c['denominator']==1 for c in r['coverage'])
    assert r['reconciliation'][0]['derived']['candidacy_ballots']==60
    t=pq.read_table(tmp_path/'out'/'congress-totals.parquet').to_pylist()
    assert t[0]['province_code']=='42' and t[0]['section_code']=='001 '
    assert t[1]['population_scope']=='cera'
    outputs=json.loads((tmp_path/'out'/'artifacts.json').read_text())
    assert all(sha256((tmp_path/'out'/p).read_bytes()).hexdigest()==h for p,h in outputs.items())
    with pytest.raises(ValueError,match='no vacío'):run(c,m,raw,tmp_path/'out','42')


def test_failure_cannot_look_like_complete_report(pipeline_inputs,tmp_path):
    c,m,raw=pipeline_inputs
    make_zip(raw/'congress.zip',duplicate=True)
    records=[json.loads(s) for s in m.read_text().splitlines()]
    for r in records:
        p=raw/r['path'];r.update(sha256=sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
    m.write_text(''.join(json.dumps(r)+'\n' for r in records))
    with pytest.raises(ValueError):run(c,m,raw,tmp_path/'out','42')
    assert (tmp_path/'out'/'FAILED.json').exists()
    assert not (tmp_path/'out'/'report.json').exists()


def test_cli_exit_codes(pipeline_inputs,tmp_path,capsys):
    c,m,raw=pipeline_inputs
    base=['--catalog',str(c)]
    paths=['--manifest',str(m),'--raw-dir',str(raw)]
    assert main(base+['verify']+paths)==0
    assert main(base+['pipeline']+paths+['--province','42','--output',str(tmp_path/'out')])==0
    assert main(base+['pipeline']+paths+['--province','1','--output',str(tmp_path/'invalid')])==2
