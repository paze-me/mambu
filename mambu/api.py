from clients import ClientsAPI
from loans import LoansAPI
from savings import SavingsAPI
from loan_transaction import LoanTransactionsAPI
from savings_transaction import SavingsTransactionsAPI
from attachments import AttachmentsAPI
from custom_fields import CustomFieldsAPI
from loan_products import LoanProductsAPI


class API(object):
    def __init__(self, config_):
        self.config = config_
        self.Clients = ClientsAPI(self)
        self.Loans = LoansAPI(self)
        self.Savings = SavingsAPI(self)
        self.LoanTransactions = LoanTransactionsAPI(self)
        self.SavingsTransactions = SavingsTransactionsAPI(self)
        self.Attachments = AttachmentsAPI(self)
        self.CustomFields = CustomFieldsAPI(self)
        self.LoanProducts = LoanProductsAPI(self)

    def get_client(self, client_id=None):
        return self.Clients.get(client_id)

    def get_loan(self, loan_id=None):
        return self.Loans.get(loan_id)

    def get_saving(self, saving_id):
        return self.Savings.get(saving_id)

    def get_attachment(self, attachment_id=None):
        return self.Attachments.get(attachment_id)

    def get_loan_product(self, loan_product_id=None):
        return self.LoanProducts.get(loan_product_id)