from util import AbstractAPI, AbstractDataObject
from tools import datelib

from tools import data

loan_transactions_metadata = data.load_yaml('loan_transactions')


class LoanTransactionsAPI(AbstractAPI):
    url = 'loans'
    sub_url = 'transactions'

    def get(self, loan_id):
        """Get details of the loan transactions i.e. statement associated with
        the loan with id loan_id

        Parameters
        ----------
        loan_id: str
            id of the loan in mambu

        Returns
        -------
        dict
        """
        return self._get(self._postfix_url(self.url, loan_id, self.sub_url))

    def post(self, loan_id, loan_transaction=None):
        """Send a post request containing the loan_transaction information to
        the url associated with loan_id

        Parameters
        ----------
        loan_id: str
            id of the loan in mambu
        loan_transaction: self.LoanTransaction
            the details of the loan transaction dependent on the type of the
            transaction itself

        Returns
        -------
        dict
        """
        return self._post(self._postfix_url(self.url, loan_id, self.sub_url),
                          data=loan_transaction)

    def approve(self, loan_id):
        """Approve the loan associated with loan_id.  For this to succeed the
         sum of all tranches of the loan must add up to the loan amount

        accountStatus for the loan must be PENDING_APPROVAL

        Parameters
        ----------
        loan_id: str
            id of the loan in mambu

        Returns
        -------
        dict
        """
        return self._standalone_type(loan_id, 'APPROVAL')

    def undo_approval(self, loan_id):
        """Undo the approval of the loan associated with loan_id

        accountStatus for the loan must be APPROVED

        Parameters
        ----------
        loan_id: str
            id of the loan in mambu

        Returns
        -------
        dict
        """
        return self._standalone_type(loan_id, 'UNDO_APPROVAL')

    def withdraw_loan(self, loan_id):
        """Withdraw/close the loan.  Loan needs to have a balance due of 0

        Parameters
        ----------
        loan_id: str
            id of the loan in mambu

        Returns
        -------
        dict
        """
        return self._standalone_type(loan_id, 'WITHDRAW')

    def reject(self, loan_id):
        """Change the status of the loan associated with loan_id to REJECTED

        Parameters
        ----------
        loan_id: str
            id for the loan in mambu

        Returns
        -------
        dict
        """
        return self._standalone_type(loan_id, 'REJECT')

    def lock(self, loan_id):
        """Lock the interest for the loan.  Loan needs to approved and account
        associated with the loan needs to be active

        Parameters
        ----------
        loan_id: str
            id of the loan in mambu

        Returns
        -------
        dict
        """
        return self._standalone_type(loan_id, 'LOCK')

    def unlock(self, loan_id):
        """Unlock a loan with loan_id that currently has the interest on the
        loan set to locked

        accountStatus must be INTEREST_LOCKED

        Parameters
        ----------
        loan_id: str    id of the loan in mambu

        Returns
        -------
        dict
        """
        return self._standalone_type(loan_id, 'UNLOCK')

    def _standalone_type(self, loan_id, transaction_type):
        """Apply the transaction_type to the loan associated with loan_id
        All these transaction types have no params associated with them

        Parameters
        ----------
        loan_id: str
            id for the loan in mambu
        transaction_type: str
            one of 'APPROVAL', 'UNDO_APPROVAL', 'WITHDRAW', 'REJECT', 'LOCK',
            'UNLOCK'

        Returns
        -------
        dict
        """
        if transaction_type not in \
                loan_transactions_metadata['transaction_types']:
            return 'Invalid transaction Type'
        return self.post(loan_id, self.LoanTransaction(type=transaction_type))

    def apply_fee(self, loan_id, amount, date=None):
        """Apply the fee to the loan associated with loan_id

        Parameters
        ----------
        loan_id: str
            id of the loan in mambu
        amount: float
            amount of the fee to apply to the loan in the local currency in
            whole units e.g. UK, 10 is equivalent to GBP10.00
        date: date, datetime, str
            date-like to coerce into datestr.  Passed to apply_fee to date
            transaction

        Returns
        -------
        dict
        """
        if date is None or datelib.coerce_date(date) == datelib.date_today():
            result = self.post(
                loan_id, self.LoanTransaction(type='FEE', amount=amount))
        else:
            date = datelib.mambu_date(date)
            result = self.post(
                loan_id, self.LoanTransaction(
                    type='FEE', amount=amount, date=date))
        return result

    def repayment(self, loan_id, amount, date=None, method=None, notes=None):
        return self.post(loan_id, self.LoanTransaction(
            type='REPAYMENT', amount=amount, date=date, method=method,
            notes=notes))

    def disburse(self, loan_id):
        #  This spelling mistake is intentional and is present in mambu
        return self.post(loan_id, self.LoanTransaction(
            type='DISBURSMENT'))

    def undo_disburse(self, loan_id):
        #  This spelling mistake is intentional and is present in mambu
        return self.post(loan_id, self.LoanTransaction(
            type='DISBURSMENT_ADJUSTMENT'))

    def disburse_with_fee(self, loan_id, fee, date=None):
        """Disburse the next tranche in the loan associated with loan_id and
        manually apply the fee specified in

        Parameters
        ----------
        loan_id: str
            if of loan in mambu
        fee: float
            amount of fee to apply to the loan in full units of currency e.g. in
            the UK fee=10 would apply a GBP10.00 fee to the loan
        date: date, datetime, str
            date-like to coerce into datestr.  Passed to apply_fee to date
            transaction

        Returns
        -------
        dict
        """
        return [self.disburse(loan_id), self.apply_fee(loan_id, fee, date)]

    class LoanTransaction(AbstractDataObject):
        fields = loan_transactions_metadata['parameters']

