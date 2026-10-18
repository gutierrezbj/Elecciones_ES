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


def make_islands_zip(path, missing_map=False):
    prefix='032023071';province='35';suffix='032307.DAT'
    def geo(municipality,district,section='0000',mesa='U'):
        return prefix+'05'+province+municipality+district+section+mesa
    def row09(g,counts):return g+''.join(f'{v:07}' for v in counts)+'S'
    def row07(district,multiplier):
        return prefix+'05'+province+district+'Las Palmas'.ljust(50)+'00000300'+f'{multiplier:05}'+''.join(f'{v*multiplier:08}' for v in [100,110,0,0,20,40,3,2,60])+'000002'+'00000000'*2+'S'
    rows05,rows09,rows10=[],[],[]
    for district in ['1','2','3']:
        municipality='00'+district
        s=list('0'*233);s[:9]=prefix;s[9:11]='05';s[11:13]=province;s[13:16]=municipality;s[16:18]='99';s[118]=district
        if not(missing_map and district=='3'):rows05.append(''.join(s))
        normal=geo(municipality,'01','001 ')
        cera=geo('999','0'+district)
        rows09.extend([row09(normal,[100,100,0,0,20,40,3,2,55,0,0]),row09(cera,[0,10,0,0,0,0,0,0,5,0,0])])
        candidate=province+district+'001'
        rows10.extend([normal+candidate+'0000055',cera+candidate+'0000005'])
    rollup=geo('999','09')
    rows09.append(row09(rollup,[0,30,0,0,0,0,0,0,15,0,0]))
    rows10.extend(rollup+province+d+'001'+'0000005' for d in ['1','2','3'])
    with ZipFile(path,'w') as z:
        z.writestr('02'+suffix,prefix+'N99'+'23072023'+'09:0020:0014:0018:00\n')
        z.writestr('05'+suffix,'\n'.join(rows05)+'\n')
        z.writestr('07'+suffix,'\n'.join([row07('9',3),*(row07(d,1) for d in ['1','2','3'])])+'\n')
        z.writestr('09'+suffix,'\n'.join(rows09)+'\n')
        z.writestr('10'+suffix,'\n'.join(rows10)+'\n')
        z.writestr('FICHEROS.doc','Synthetic fixture')
    return path
