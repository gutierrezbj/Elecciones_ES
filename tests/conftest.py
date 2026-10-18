from hashlib import sha256
import json
from zipfile import ZipFile
import pytest


@pytest.fixture
def total():
    return dict(election_date='2023-07-23', election_type='congress', scrutiny_type='definitive',
        geography_level='table', province_code='42', municipality_code='001', district_code='01',
        section_code='001 ', table_code='U', population_scope='cer', source_id='synthetic',
        source_locators=['09.DAT:line:1'], electors=100, voters=60, valid_votes=58,
        null_votes=2, blank_votes=3, candidacy_ballots=55)


@pytest.fixture
def result(total):
    base={k:v for k,v in total.items() if k not in {'electors','voters','valid_votes','null_votes','blank_votes','candidacy_ballots'}}
    return dict(base,candidacy_key='000001',candidacy_code='000001',candidate_code=None,votes=55)


def make_zip(path, chamber='congress', *, duplicate=False, orphan=False, official='S', malformed=False, missing_candidate=False):
    code = '02' if chamber == 'congress' else '03'
    prefix=code+'2023071'
    geography=prefix+'08'+'42'+'001'+'01'+'001 '+'U'
    cera=prefix+'08'+'42'+'999'+'09'+'0000'+'U'
    # 09: electors INE, scrutiny, CERE, voters CERE, advances, blank, null, candidacy, referendum x2
    physical=geography+''.join(f'{v:07}' for v in [100,100,0,0,20,40,3,2,55,0,0])+official
    overseas=cera+''.join(f'{v:07}' for v in [0,10,0,0,0,0,0,0,5,0,0])+official
    published=prefix+'08'+'42'+'9'+'Soria'.ljust(50)+'00000100'+'00001'+''.join(f'{v:08}' for v in [100,110,0,0,20,40,3,2,60])+'000002'+'00000000'*2+official
    identification=prefix+'N99'+'23072023'+'09:0020:0014:0018:00'
    identifier='000001' if chamber=='congress' else '429001'
    r=geography+identifier+'0000055'
    if orphan:r=r[:13]+'002'+r[16:]
    if malformed:r=r[:-1]
    suffix=code+'2307.DAT'
    with ZipFile(path,'w') as z:
        z.writestr('02'+suffix,identification+'\n')
        z.writestr('07'+suffix,published+'\n')
        z.writestr('09'+suffix,physical+'\n'+overseas+'\n'+(physical+'\n' if duplicate else ''))
        z.writestr('10'+suffix,('' if missing_candidate else r+'\n')+cera+identifier+'0000005\n')
        z.writestr('04'+suffix,'PERSONAL FILE MUST NEVER BE READ')
        z.writestr('FICHEROS.doc',b'Synthetic format fixture, no official data')
    return path


@pytest.fixture
def zip_factory(tmp_path):
    def make(**kw):return make_zip(tmp_path/(kw.get('chamber','congress')+'.zip'),**kw)
    return make
