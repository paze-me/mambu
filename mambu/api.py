from clients import ClientsAPI
from loans import LoansAPI
from attachments import AttachmentsAPI
from util import AbstractAPI
from tools import datelib


class API(AbstractAPI):
    def __init__(self, config_):
        super(API, self).__init__(config_=config_)
        self.config = config_
        self.Clients = ClientsAPI(self)
        self.Loans = LoansAPI(self)
        self.Attachments = AttachmentsAPI(self)

    def get_client(self, client_id=None):
        return self.Clients.get(client_id)

    def get_loan(self, loan_id=None):
        return self.Loans.get(loan_id)

    def get_savings(self, saving_id=None, params=None):
        return self._get(self._url_savings(saving_id), params=params)

    def get_savings_transactions(self, savings_id):
        return self._get(self._url_savings_transactions(savings_id))

    def get_attachment(self, attachment_id=None):
        return self.Attachments.get(attachment_id)

    def get_loan_product(self, loan_product_id=None):
        return self._get(self._url_loan_products(loan_product_id))

    def get_loan_product_encoded_key(self, loan_product_id=None):
        loan_product = self.get_loan_product(loan_product_id)
        return loan_product['encodedKey']

    def get_custom_field(self, custom_field_id):
        return self._get(self._postfix_url('customfields'))

    def get_transactions(self, loan_id):
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
        return self._get(self._url_loan_transactions(loan_id))

    def _post_loan_transaction(self, loan_id, loan_transaction):
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
        return self._post(self._url_loan_transactions(loan_id),
                          data=loan_transaction)

    def custom_field_sets(self, _type=None):
        url = 'customfieldsets' + '' if _type is None else '?type=%s' % _type
        return self._get(url)

    def create_client(self, *args, **kwargs):
        return self.Clients.create(*args, **kwargs)

    def create_loan(self, *args, **kwargs):
        return self.Loans.create(*args, **kwargs)

    def create_savings(self, savings_account, custom_information=None):
        return self._post(self._url_savings(), data=dict(
            savingsAccount=savings_account,
            customInformation=custom_information))

    def create_savings_transaction(self, savings_id, savings_transaction=None):
        return self._post(self._url_savings_transactions(
            savings_id, savings_transaction))

    def update_savings(
            self, savings_id, savings_account, custom_information=None):
        return self._post(self._url_savings_transactions(savings_id),
                          data=dict(savingsAccount=savings_account,
                                    customInformation=custom_information))

    def savings_set_custom_field(self, savings_id, custom_field_id, value):
        return self._patch(self._url_savings_custom_field(
            savings_id, custom_field_id), data={'value': value})

    def savings_delete_custom_field(self, savings_id, custom_field_id):
        return self._delete(
            self._url_savings_custom_field(savings_id, custom_field_id))

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
        return self._post_loan_transaction(loan_id, dict(type='APPROVAL'))

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
        return self._post_loan_transaction(loan_id, dict(type='UNDO_APPROVAL'))

    def withdraw(self, loan_id):
        """Withdraw/close the loan.  Loan needs to have a balance due of 0

        Parameters
        ----------
        loan_id: str
            id of the loan in mambu

        Returns
        -------
        dict
        """
        return self._post_loan_transaction(loan_id, dict(type='WITHDRAW'))

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
        return self._post_loan_transaction(loan_id, dict(type='REJECT'))

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
        return self._post_loan_transaction(loan_id, dict(type='LOCK'))

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
        return self._post_loan_transaction(loan_id, dict(type='UNLOCK'))

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
            result = self._post_loan_transaction(
                loan_id, dict(type='FEE', amount=amount))
        else:
            date = datelib.mambu_date(date)
            result = self._post_loan_transaction(
                loan_id, dict(type='FEE', amount=amount, date=date))
        return result

    def repayment(self, loan_id, amount, date=None, method=None, notes=None):
        return self._post_loan_transaction(loan_id, dict(
            type='REPAYMENT', amount=amount, date=date, method=method,
            notes=notes))

    def disburse(self, loan_id):
        #  This spelling mistake is intentional and is present in mambu
        return self._post_loan_transaction(loan_id, dict(type='DISBURSMENT'))

    def undo_disburse(self, loan_id):
        #  This spelling mistake is intentional and is present in mambu
        return self._post_loan_transaction(
            loan_id, dict(type='DISBURSMENT_ADJUSTMENT'))

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

    def _url_savings(self, savings_id=None):
        return self._postfix_url('savings', savings_id)

    def _url_savings_custom_field(self, savings_id, custom_field_id):
        return self._postfix_url(
            self._url_savings(savings_id), 'custominformation', custom_field_id)

    def _url_savings_transactions(self, savings_id, transactions_id=None):
        return self._postfix_url(
            'savings', savings_id, 'transactions', transactions_id)

    def _url_loan_products(self, loan_product_id=None):
        return self._postfix_url('loanproducts', loan_product_id)

    def _url_loans(self, loan_id=None):
        return self._postfix_url('loans', loan_id)

    def _url_loan_transactions(self, loan_id):
        return self._postfix_url(self._url_loans(loan_id), 'transactions')
