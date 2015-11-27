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
