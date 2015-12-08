import pytest


@pytest.mark.slow
def test_transactions(mambuapi):
    loans = mambuapi.get_loan(None)
    if len(loans) > 0:
        assert mambuapi.get_transactions(loans[0]['id']) is not None


@pytest.mark.slow
def test_create_transaction(mambuapi, unapproved_loan):
    result = mambuapi.approve(unapproved_loan['id'])
    assert result['accountState'] == 'APPROVED'
    assert result['loanAmount'] == '1200'


@pytest.mark.slow
def test_standalone_types(mambuapi, loan_dict, unapproved_loan):
    loan_id = unapproved_loan['id']
    amount = loan_dict['tranches'][0]['amount']
    result = mambuapi.approve(loan_id)
    assert result['accountState'] == 'APPROVED'
    result = mambuapi.undo_approval(loan_id)
    assert result['accountState'] == 'PENDING_APPROVAL'
    result = mambuapi.approve(loan_id)
    assert result['accountState'] == 'APPROVED'
    result = mambuapi.disburse(loan_id)
    assert result['balance'] == result['amount'] == amount
    assert result['principalPaid'] == amount
    assert result['type'] == 'DISBURSMENT'
    result = mambuapi.lock(loan_id)
    assert result[0]['type'] == 'INTEREST_LOCKED'
    result = mambuapi.unlock(loan_id)
    assert result[0]['type'] == 'INTEREST_UNLOCKED'


@pytest.mark.slow
def test_disburse_apply_fee(mambuapi, approved_loan):
    loan_id = approved_loan['id']
    _fee = 10
    result = mambuapi.disburse(loan_id)
    assert result['type'] == 'DISBURSMENT'
    loan_after = mambuapi.get_loan(loan_id)
    net = float(approved_loan['principalBalance']) + float(result['balance'])
    assert net == float(loan_after['principalBalance'])
    result = mambuapi.apply_fee(loan_id, _fee)
    assert result['amount'] == str(_fee)
    loan_after_fee = mambuapi.get_loan(loan_id)
    net = float(approved_loan['feesDue']) + _fee
    assert net == float(loan_after_fee['feesDue'])


@pytest.mark.slow
def test_disburse_with_fee(mambuapi, approved_loan):
    loan_id = approved_loan['id']
    datestr = approved_loan['tranches'][0]['expectedDisbursementDate']
    fee = 4.00
    result = mambuapi.disburse_with_fee(loan_id, fee, datestr)
    loan_after = mambuapi.get_loan(loan_id)
    assert float(approved_loan['principalBalance']
                 ) + float(result[0]['balance']) == float(
        loan_after['principalBalance'])
    assert float(approved_loan['feesDue']
                 ) + fee == float(loan_after['feesDue'])


@pytest.mark.slow
def test_disburse_today(mambuapi, approved_loan_start_today):
    loan = approved_loan_start_today
    loan_id = loan['id']
    result = mambuapi.disburse(loan_id)
    loan_after = mambuapi.get_loan(loan_id)
    net = float(loan['principalBalance']) + float(result['balance'])
    assert net == float(loan_after['principalBalance'])


@pytest.mark.slow
def test_disburse_set_repayment(mambuapi, approved_loan):
    loan_id = approved_loan['id']
    mambuapi.disburse(loan_id, first_repayment_date='2015-09-25')
    loans = mambuapi.get_repayments_due_on_date('2015-09-25')
    assert loan_id in map(lambda x: x['id'], loans)
