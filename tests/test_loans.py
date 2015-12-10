import pytest

from mambu.tools import datelib


@pytest.mark.slow
def test_loans1(mambuapi, unapproved_loan):
    loan_id = unapproved_loan['id']
    loans = mambuapi.get_loan(None)
    assert loans is not None
    assert loan_id in map(lambda x: x['id'], loans)


@pytest.mark.slow
def test_loan2(mambuapi, unapproved_loan):
    loan_id = unapproved_loan['id']
    assert mambuapi.get_loan(loan_id)['id'] == loan_id


@pytest.mark.slow
def test_loans_for_client(mambuapi, user_in_mambu_id, unapproved_loan):
    loan_id = unapproved_loan['id']
    loans = mambuapi.get_loans_by_entity('clients', user_in_mambu_id)
    assert loan_id in map(lambda x: x['id'], loans)


@pytest.mark.slow
def test_create_loan(mambuapi, loan_dict):
    loan_account = mambuapi.create_loan(loan_dict)['loanAccount']
    tranches = loan_dict.pop('tranches')
    for k, v in loan_dict.iteritems():
        assert loan_account[k] == v, 'Created account does not match passed parameters for field %s' % k
    for n, tranche in enumerate(tranches):
        t = loan_account['tranches'][n]
        assert float(t['amount']) == float(tranche['amount'])
        assert datelib.coerce_date(
            t['expectedDisbursementDate']
        ) == datelib.coerce_date(tranche['expectedDisbursementDate'])


@pytest.mark.slow
def test_custom_field(mambuapi, unapproved_loan):
    field_name = 'l_advance_cycle'
    field_value = '1111'
    loan_id = unapproved_loan['id']
    set_result = mambuapi.set_loan_custom_field(
        loan_id, field_name, field_value)
    assert set_result['returnCode'] == 0
    updated_loan = mambuapi.get_loan_full_details(loan_id)
    assert updated_loan['id'] == loan_id
    custom_fields = updated_loan['customFieldValues']
    assert len(custom_fields) == 1
    assert custom_fields[0]['customFieldID'] == field_name
    assert custom_fields[0]['value'] == field_value
    delete_result = mambuapi.delete_loan_custom_field(
        loan_id, 'l_advance_cycle')
    assert delete_result['returnCode'] == 0
    after_delete_loan = mambuapi.get_loan_full_details(loan_id)
    assert after_delete_loan['customFieldValues'] == []


@pytest.mark.slow
def test_get_loans_by_single_filter(mambuapi, unapproved_loan):
    loans = mambuapi.get_loans_by_single_filter(
        'LOAN_AMOUNT', 'BETWEEN', 0, 1500)
    assert len(loans) > 0


@pytest.mark.slow
def test_get_loans_by_filter_constraints(mambuapi, unapproved_loan):
    loan_id = unapproved_loan['id']
    loan_amount = unapproved_loan['loanAmount']
    filter_constraints = [
        dict(filterSelection='ACCOUNT_ID', filterElement='EQUALS',
             value=loan_id),
        dict(filterSelection='LOAN_AMOUNT', filterElement='EQUALS',
             value=loan_amount)]
    loans = mambuapi.get_loans_by_filter_constraints(filter_constraints)
    assert loan_id in map(lambda x: x['id'], loans)


@pytest.mark.slow
def test_get_disbursements_due_today(mambuapi):
    loans = mambuapi.get_disbursements_due_today()
    assert loans is not None


@pytest.mark.slow
def test_get_disbursements_due_on_date(mambuapi, unapproved_loan):
    test_date = unapproved_loan['expectedDisbursementDate']
    loans = mambuapi.get_disbursements_due_on_date(test_date)
    assert len(loans) > 0


@pytest.mark.slow
def test_get_disbursements_due_in_xbdays(mambuapi):
    loans = mambuapi.get_disbursements_due_in_xbdays(3)
    assert loans is not None


@pytest.mark.slow
def test_get_principals_due_today(mambuapi):
    """Very basic call to loan"""
    loans = mambuapi.get_principals_due_today()
    assert loans is not None


@pytest.mark.slow
def test_get_principals_due_on_date(mambuapi):
    loans = mambuapi.get_principals_due_on_date('2015-11-10')
    assert loans is not None


@pytest.mark.slow
def test_get_principals_due_in_xbdays(mambuapi):
    loans = mambuapi.get_principals_due_in_xbdays(3)
    assert loans is not None


@pytest.mark.slow
def test_get_transactions(mambuapi, approved_loan):
    _fee = 5
    loan_id = approved_loan['id']
    datestr = approved_loan['tranches'][0]['expectedDisbursementDate']
    mambuapi.disburse_with_fee(loan_id, _fee, datestr)
    transactions = mambuapi.get_transactions(loan_id)
    assert len(transactions) == 2
    assert transactions[0]['type'] == 'FEE'
    assert int(transactions[0]['amount']) == _fee
    assert transactions[1]['type'] == 'DISBURSMENT'
    assert transactions[1]['amount'] == approved_loan['tranches'][0]['amount']
