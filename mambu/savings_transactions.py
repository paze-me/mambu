from util import *
from tools import data

savings_transactions_metadata = data.load_yaml('savings_transactions.yaml')


class SavingsTransactionsAPI(AbstractAPI):
    url = 'savings'

    def get(self, savings_id):
        return self._get(
            self._postfix_url(self.url, savings_id, 'transactions'))

    def create(self, savings_id, savings_transaction=None):
        return self._post(self._postfix_url(
            self.url, savings_id, 'transactions', savings_transaction))

    class SavingsTransaction(AbstractDataObject):
        fields = savings_transactions_metadata['transactions']
