from clients import ClientsAPI
from loans import LoansAPI
from savings import SavingsAPI
from loan_transaction import LoanTransactionsAPI
from attachments import AttachmentsAPI
from custom_fields import CustomFieldsAPI
from util import AbstractAPI


class API(AbstractAPI):
    def __init__(self, config_):
        super(API, self).__init__(config_=config_)
        self.config = config_
        self.Clients = ClientsAPI(self)
        self.Loans = LoansAPI(self)
        self.Savings = SavingsAPI(self)
        self.LoanTransactions = LoanTransactionsAPI(self)
        self.Attachments = AttachmentsAPI(self)
        self.CustomFields = CustomFieldsAPI(self)

    def get_client(self, client_id=None):
        return self.Clients.get(client_id)

    def get_loan(self, loan_id=None):
        return self.Loans.get(loan_id)

    def get_saving(self, saving_id):
        return self.Savings.get(saving_id)

    def get_savings_transactions(self, savings_id):
        return self._get(self._url_savings_transactions(savings_id))

    def get_attachment(self, attachment_id=None):
        return self.Attachments.get(attachment_id)

    def get_loan_product(self, loan_product_id=None):
        return self._get(self._url_loan_products(loan_product_id))

    def get_loan_product_encoded_key(self, loan_product_id=None):
        loan_product = self.get_loan_product(loan_product_id)
        return loan_product['encodedKey']

    def get_loan_transactions(self):
        pass

    def create_client(self, *args, **kwargs):
        return self.Clients.create(*args, **kwargs)

    def create_loan(self, *args, **kwargs):
        return self.Loans.create(*args, **kwargs)

    def create_savings_transaction(self, savings_id, savings_transaction=None):
        return self._post(self._url_savings_transactions(
            savings_id, savings_transaction))

    def approve_loan(self, loan_id):
        return self.LoanTransactions.approve(loan_id)

    def apply_fee(self, loan_id, amount, date):
        return self.LoanTransactions.apply_fee(loan_id, amount, date)

    def disburse(self, loan_id):
        return self.LoanTransactions.disburse(loan_id)

    def _url_savings_transactions(self, savings_id, transactions_id=None):
        return self._postfix_url(
            'savings', savings_id, 'transactions', transactions_id)

    def _url_loan_products(self, loan_product_id=None):
        return self._postfix_url('loanproducts', loan_product_id)
