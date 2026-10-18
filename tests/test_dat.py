import pytest
from zipfile import ZipFile
from elecciones.dat import read_dat
from elecciones.validation import validate


def source(chamber='congress'):return {'id':'synthetic','election_type':chamber}


def test_real_format_synthetic_fixture(zip_factory):
    t,r,p,n=read_dat(zip_factory(),source(),'42');r=list(r)
    assert len(t)==2 and len(r)==2 and len(p)==1
    assert t[0]['section_code']=='001 ' and t[0]['municipality_code']=='001'
    assert t[1]['geography_level']=='cera' and t[1]['municipality_code']=='999'
    assert t[0]['official_flag']=='S' and t[0]['scrutiny_type']=='definitive'
    assert r[0]['candidacy_code']=='000001' and r[0]['candidate_code'] is None
    assert validate(t,r)==[]


def test_senate_candidate_code_without_names(zip_factory):
    t,r,p,n=read_dat(zip_factory(chamber='senate'),source('senate'),'42');r=list(r)
    assert r[0]['candidate_code']=='429001' and r[0]['candidacy_code'] is None
    assert not any('name' in k for row in r for k in row)


def test_nonofficial_flag_is_not_assumed_provisional(zip_factory):
    t,r,p,n=read_dat(zip_factory(official='N'),source(),'42')
    assert t[0]['scrutiny_type']=='unknown'
    assert list(r)[0]['scrutiny_type']=='unknown'


@pytest.mark.parametrize('option',['duplicate','orphan','malformed'])
def test_reject_invalid_records(zip_factory,option):
    with pytest.raises(ValueError):
        t,r,p,n=read_dat(zip_factory(**{option:True}),source(),'42');list(r)


def test_candidate_row_missing_detected(zip_factory):
    t,r,p,n=read_dat(zip_factory(missing_candidate=True),source(),'42')
    assert any(f['rule']=='candidacy_sum' for f in validate(t,r))


def test_island_cera_rollup_not_double_counted(zip_factory):
    p=zip_factory(chamber='senate')
    with ZipFile(p,'a') as z:
        row=z.read('09032307.DAT').splitlines()[1]
        island=row[:16]+b'01'+row[18:]
        # Add an auxiliary member rather than replacing the existing one.
        data={n:z.read(n) for n in z.namelist()}
    data['09032307.DAT']+=island+b'\n'
    with ZipFile(p,'w') as z:
        for n,v in data.items():z.writestr(n,v)
    t,r,published,notes=read_dat(p,source('senate'),'42')
    assert len(t)==2 and len(notes)==1
    assert notes[0]['rule']=='excluded_cera_rollup'
    assert len(list(r))==2


def test_senate_islands_preserve_cera_and_constituencies(tmp_path):
    from conftest import make_islands_zip
    t,results,published,notes=read_dat(make_islands_zip(tmp_path/'islands.zip'),source('senate'),'35')
    results=list(results)
    assert len(t)==6 and len(results)==6 and len(published)==4
    assert {r['district_code'] for r in t if r['geography_level']=='cera'}=={'01','02','03'}
    assert all(r['candidate_code'][2]==r['constituency_code'] for r in results)
    assert sum(r['candidacy_ballots'] for r in t)==180
    assert len(notes)==1
    assert {r['constituency_code'] for r in published}=={'9','1','2','3'}
    assert validate(t,results)==[]


def test_insular_mapping_is_required_not_guessed(tmp_path):
    from conftest import make_islands_zip
    with pytest.raises(ValueError,match='No se puede asignar'):
        read_dat(make_islands_zip(tmp_path/'islands.zip',missing_map=True),source('senate'),'35')
