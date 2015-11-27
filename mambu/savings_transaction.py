from util import *

class SavingsTransactionsAPI(AbstractAPI):
    url = 'savings'

    def get(self, id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._savings_trans_url(id))

    def create(self, id, savingsTransaction = None):
        """
            id : integer or string
            savingsTransaction : SavingsTransaction
        """
        return self._request('post', self._savings_trans_url(id), savingsTransaction)

    def _savings_trans_url(self, id):
        url_ = self.url + '/' + str(id) + '/transactions'
        return url_

    class SavingsTransaction(AbstractDataObject):
        fields = ['type','amount','toSavingsAccount','toLoanAccount','date','method','identifier','accountName',
                  'receiptNumber','bankNumber','checkNumber','bankAccountNumber','bankRoutingNumber','notes']

