import pytest


@pytest.mark.slow
def test_transactions(mambuapi):
    loans = mambuapi.Loans.get(None)
    if len(loans) > 0:
        assert mambuapi.LoanTransactions.get(loans[0]['id']) != None


@pytest.mark.slow
def test_create_transaction(mambuapi, user_in_mambu):
        loan = {
            "accountHolderType": "CLIENT",
            "productTypeKey": "8a1a2fbd4f1c1730014f27fa48602746",
            "accountHolderKey": user_in_mambu.encodedkey,
            "repaymentInstallments": 1,
            "loanAmount": "1200",
            "interestRate": "0",
            "repaymentPeriodCount": 1,
            "repaymentPeriodUnit": "MONTHS",
            "tranches": [
                {
                    "amount": "400",
                    "expectedDisbursementDate": "2015-09-04T00:00:00+0000"
                },
                {
                    "amount": "400",
                    "expectedDisbursementDate": "2015-09-11T00:00:00+0000"
                },
                {
                    "amount":"400",
                    "expectedDisbursementDate": "2015-09-18T00:00:00+0000"
                }
            ]
        }

        loan = mambuapi.Loans.create(loan)
        transaction = {
            "type": "APPROVAL"
        }
        result = mambuapi.LoanTransactions.post(loan['loanAccount']['encodedKey'],
                                         transaction)
        assert result['accountState'] == 'APPROVED'
        assert result['loanAmount'] == '1200'


@pytest.mark.xfail
@pytest.mark.slow
def test_standalone_types(mambuapi, unapproved_loan_id):
    loan_id = unapproved_loan_id
    result = mambuapi.LoanTransactions.approve(loan_id)
    assert result['accountState'] == 'APPROVED'
    result = mambuapi.LoanTransactions.undo_approval(loan_id)
    assert result['accountState'] == 'PENDING_APPROVAL'
    result = mambuapi.LoanTransactions.approve(loan_id)
    assert result['accountState'] == 'APPROVED'
    # ToDo Needs a loan which has started to be disbursed or a user active
    # result = mambuapi.LoanTransactions.lock(loan_id)
    # assert result[0]['type'] == 'INEREST_LOCKED'
    # result = mambuapi.LoanTransactions.unlock(loan_id)
    # assert result[0]['type'] == 'INEREST_UNLOCKED'
    # result = mambuapi.LoanTransactions.withdraw_loan(loan_id)
    # assert result['accountState'] == 'WITHDRAWN'
    # ToDo need to check if loan status can be set to reject from withdraw
    # result = mambuapi.LoanTransactions.withdraw_loan(loan_id)



@pytest.mark.xfail
@pytest.mark.slow
def test_apply_fee(mambuapi, mambu_approved_loan):
    loan_id = mambu_approved_loan['id']
    loan_amount = 10
    result = mambuapi.LoanTransactions.apply_fee(loan_id, loan_amount)
    assert result['amount'] == str(loan_amount)
    loan_after = mambuapi.Loans.get(loan_id)
    assert float(mambu_approved_loan['feesDue']
                 ) + loan_amount == float(loan_after['feesDue'])


@pytest.mark.slow
def test_disburse(mambuapi, mambu_approved_loan):
    loan_id = mambu_approved_loan['id']
    result = mambuapi.LoanTransactions.disburse(loan_id)
    loan_after = mambuapi.Loans.get(loan_id)
    assert float(mambu_approved_loan['principalBalance']
                 ) + float(result['balance']) == float(loan_after['principalBalance'])


@pytest.mark.slow
def test_disburse_with_fee(mambuapi, mambu_approved_loan):
    loan_id = mambu_approved_loan['id']
    datestr = mambu_approved_loan['tranches'][0]['expectedDisbursementDate']
    fee = 4.00
    result = mambuapi.LoanTransactions.disburse_with_fee(loan_id, fee, datestr)
    loan_after = mambuapi.Loans.get(loan_id)
    assert float(mambu_approved_loan['principalBalance']
                 ) + float(result[0]['balance']) == float(
        loan_after['principalBalance'])
    assert float(mambu_approved_loan['feesDue']
                 ) + fee == float(loan_after['feesDue'])


@pytest.mark.slow
def test_disburse_today(mambuapi, mambu_approved_loan_start_today):
    loan_id = mambu_approved_loan_start_today['id']
    result = mambuapi.LoanTransactions.disburse(loan_id)
    loan_after = mambuapi.Loans.get(loan_id)
    assert float(mambu_approved_loan_start_today['principalBalance']
                 ) + float(result['balance']) == float(loan_after['principalBalance'])
