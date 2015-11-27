import pytest

from tools import datelib


@pytest.mark.slow
def test_loans(mambuapi):
    assert mambuapi.Loans.get(None) != None


@pytest.mark.slow
def test_loan(mambuapi):
    loans = mambuapi.Loans.get(None)
    if len(loans)>0:
        assert mambuapi.Loans.get(loans[0]['id']) != None


@pytest.mark.slow
def test_loans_for_client(mambuapi):
    clients = mambuapi.Clients.get(None)
    if len(clients) > 0:
        assert mambuapi.Loans.get_for_client(clients[0]['id']) != None


@pytest.mark.slow
def test_create_loan(mambuapi, loan_dict):
    loan_account = mambuapi.Loans.create(loan_dict)['loanAccount']
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
def test_custom_field(mambuapi):
    loans = mambuapi.Loans.get()
    if len(loans) > 0:
        mambuapi.Loans.set_custom_field(loans[0]['id'], 'l_advance_cycle', '1111')
        mambuapi.Loans.delete_custom_field(loans[0]['id'], 'l_advance_cycle')


@pytest.mark.slow
def test_get_loans_by_filter_field(mambuapi):
    """Very basic test of general use of filter field"""
    loans = mambuapi.Loans.get_loans_by_filter_field(
        'LOAN_AMOUNT', 'BETWEEN', 0, 1000)


@pytest.mark.slow
def test_get_disbursements_due_today(mambuapi):
    """Very basic call to loan"""
    loans = mambuapi.Loans.get_disbursements_due_today()


@pytest.mark.slow
def test_get_disbursements_due_on_date(mambuapi):
    """Very basic call to loan on date"""
    loans = mambuapi.Loans.get_disbursements_due_on_date('2015-11-10')


@pytest.mark.slow
def test_get_disbursements_due_in_xbdays(mambuapi):
    loans = mambuapi.Loans.get_disbursements_due_in_xbdays(3)


@pytest.mark.slow
def test_get_principals_due_today(mambuapi):
    """Very basic call to loan"""
    loans = mambuapi.Loans.get_principals_due_today()


@pytest.mark.slow
def test_get_principals_due_on_date(mambuapi):
    loans = mambuapi.Loans.get_principals_due_on_date('2015-11-10')


@pytest.mark.slow
def test_get_principals_due_in_xbdays(mambuapi):
    loans = mambuapi.Loans.get_principals_due_in_xbdays(3)


@pytest.mark.slow
def test_get_transactions(mambuapi, mambu_approved_loan):
    _fee = 5
    loan_id = mambu_approved_loan['id']
    datestr = mambu_approved_loan['tranches'][0]['expectedDisbursementDate']
    mambuapi.LoanTransactions.disburse_with_fee(loan_id, _fee, datestr)
    transactions = mambuapi.Loans.get_transactions(loan_id)
    t = transactions[0]
    assert t['type'] == 'FEE'
    assert int(t['amount']) == _fee
