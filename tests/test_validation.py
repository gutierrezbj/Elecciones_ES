import pytest
from elecciones.validation import validate, compare_totals, coverage


def rules(t,r):return {f['rule'] for f in validate(t,r)}


def test_balanced_synthetic(total,result):
    assert validate([total],[result])==[]


def test_duplicate_keys(total,result):
    assert 'duplicate_key' in rules([total,total],[result])
    assert 'duplicate_key' in rules([total],[result,result])


def test_same_candidate_in_different_table_is_not_duplicate(total,result):
    other=dict(total,table_code='A');other_result=dict(result,table_code='A')
    assert validate([total,other],[result,other_result])==[]


@pytest.mark.parametrize('field,value,rule',[('votes',-1,'invalid_count'),('votes',True,'invalid_count'),('votes',None,'invalid_count'),('votes',54,'candidacy_sum'),('section_code','001A',None),('section_code','001 ','none'),('province_code','1','invalid_geography_code')])
def test_counts_and_codes(total,result,field,value,rule):
    modified=dict(result,**{field:value})
    seen=rules([total],[modified])
    if rule not in {None,'none'}:assert rule in seen
    else:assert 'invalid_geography_code' not in seen


def test_sum_identities_and_census(total,result):
    assert 'valid_plus_null' in rules([dict(total,voters=59)],[result])
    assert 'candidacy_plus_blank' in rules([dict(total,blank_votes=4)],[result])
    assert 'voters_exceed_electors' in rules([dict(total,electors=50)],[result])


def test_missing_candidate_rows_detected(total):
    assert 'candidacy_sum' in rules([total],[])


def test_senate_marks_are_not_ballots(total,result):
    t=dict(total,election_type='senate');r=dict(result,election_type='senate',votes=40,candidate_code='429001',candidacy_key=None,candidacy_code=None)
    assert validate([t],[r,dict(r,candidate_code='429002')])==[]


@pytest.mark.parametrize('changes',[{'election_type':'senate'},{'scrutiny_type':'provisional'}, {'population_scope':'cera'}, {'province_code':'28'}, {'election_date':'2019-11-10'}])
def test_only_comparable_totals(total,changes):
    with pytest.raises(ValueError):compare_totals(total,dict(total,**changes))


def test_discrepancy_is_technical_review(total):
    f=compare_totals(total,dict(total,voters=61))[0]
    assert f['rule']=='published_total_mismatch' and f['status']=='detected'
    assert f['severity']=='technical_review' and f['reviewer'] is None


def test_missing_tables_with_and_without_independent_ids():
    a=coverage(['a','a'],['a','b']);assert a['missing']==1 and a['missing_keys']==['b']
    b=coverage(['a'],denominator=2);assert b['missing']==1 and b['missing_keys'] is None
    assert coverage(['a'])['denominator'] is None
    assert coverage(['a'],['b'])['unexpected_keys']==['a']


def test_individual_senate_candidate_limit_and_orphan(total,result):
    t=dict(total,election_type='senate')
    r=dict(result,election_type='senate',candidate_code='429001',candidacy_key=None,candidacy_code=None,votes=56)
    assert 'candidate_votes_exceed_ballots' in rules([t],[r])
    assert 'orphan_result' in rules([total],[dict(result,municipality_code='002')])
