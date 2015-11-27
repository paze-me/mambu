import pytest

LOAN_ID = 'NTXPP381'
FEE = 4
REPAYMENT_AMOUNT = 1200 + 3 * FEE


@pytest.mark.demo
def test_setup_unapproved_loan(mambu_unapproved_loan):
    print ''
    print ''
    print mambu_unapproved_loan['id']
    print ''


@pytest.mark.demo
def test_approve_loan(mambuapi):
    result = mambuapi.LoanTransactions.approve(LOAN_ID)


@pytest.mark.demo
def test_undo_approve_loan(mambuapi):
    result = mambuapi.LoanTransactions.undo_approve(LOAN_ID)


@pytest.mark.demo
def test_disburse1(mambuapi):
    result = mambuapi.LoanTransactions.disburse(LOAN_ID)


@pytest.mark.demo
def test_disburse_with_fee2(mambuapi):
    result = mambuapi.LoanTransactions.disburse_with_fee(LOAN_ID, FEE)


@pytest.mark.demo
def test_disburse_all3(mambuapi):
    loan = mambuapi.Loans.get(LOAN_ID)
    tranches = loan['tranches']
    pending_tranches = filter(lambda x: 'disbursementTransactionKey' not in x,
                              tranches)
    result = [mambuapi.LoanTransactions.disburse(LOAN_ID)
              for _ in range(len(pending_tranches))]


@pytest.mark.demo
def test_disburse_all_with_fee4(mambuapi):
    loan = mambuapi.Loans.get(LOAN_ID)
    tranches = loan['tranches']
    pending_tranches = filter(lambda x: 'disbursementTransactionKey' not in x,
                              tranches)
    result = [mambuapi.LoanTransactions.disburse_with_fee(
        LOAN_ID, FEE, tranche['expectedDisbursementDate'])
              for tranche in pending_tranches]


@pytest.mark.demo
def test_make_repayment(mambuapi):
    result = mambuapi.LoanTransactions.repayment(LOAN_ID, REPAYMENT_AMOUNT)


