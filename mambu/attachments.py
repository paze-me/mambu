from util import *
import base64

class AttachmentsAPI(AbstractAPI):
    url = 'documents'

    def get(self, id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._documents_url(id))

    def getForClient(self,id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._documents_entity_url('clients', id))

    def getForGroup(self,id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._documents_entity_url('groups', id))

    def getForSaving(self, id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._documents_entity_url('savings', id))

    def getForLoan(self,id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._documents_entity_url('loans', id))

    def getForSavingProduct(self,id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._documents_entity_url('savingsProducts', id))

    def getForLoanProduct(self,id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._documents_entity_url('loanProducts', id))

    def getForBranch(self,id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._documents_entity_url('branches', id))

    def getForCenter(self,id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._documents_entity_url('centres', id))

    def getForUser(self,id):
        """
        Parameters:
          id : integer or string
        """
        return self._request('get', self._documents_entity_url('users', id))

    def create(self, document, documentContent):
        """
        Parameters:
          document : Document
          documentContent: string
        """
        return self._request('post', self._documents_url(), data = {'document' : document, 'documentContent' : base64.b64encode(documentContent)})

    def delete(self, id):
        """
        Parameters:
          id: integer or string
        """
        return self._request('delete', self._documents_url(id))
        
    def _documents_url(self,id = None):
        url_ = self.url
        if id: url_ += '/' + str(id)
        return url_

    def _documents_entity_url(self, entity, id):
        url_ = entity + '/' + str(id) + '/' + self.url
        return url_
        
    class Document:
        fields = ['documentHolderKey','documentHolderType','name','type']