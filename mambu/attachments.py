from util import *
import base64


class AttachmentsAPI(AbstractAPI):
    url = 'documents'

    def get(self, attachment_id):
        return self._request('get', self._documents_url(attachment_id))

    def _get(self, url):
        return self._request('get', url)

    def post(self, document, document_content):
        return self._request(
            'post', self._documents_url(), dict(
                document=document,
                documentContent=base64.b64encode(document_content)))

    def get_by_entity(self, entity, entity_id):
        entities = ['clients', 'groups', 'savings', 'loans', 'savingsProducts',
                    'loanProducts', 'branches', 'centres', 'users']
        if entity not in entities:
            raise Exception('{} not found.  Must be one of {}'.format(
                entity, entities))
        return self._get('{}/{}/{}'.format(entity, entity_id, self.url))

    def delete(self, attachment_id):
        return self._request('delete', self._documents_url(attachment_id))
        
    def _documents_url(self, document_id=None):
        url_ = self.url
        if document_id:
            url_ += '/{}'.format(document_id)
        return url_

    def _entity_url(self, entity, entity_id):
        url_ = '{}/{}/{}'.format(entity, entity_id, self.url)
        return url_
        
    class Document:
        fields = ['documentHolderKey', 'documentHolderType', 'name', 'type']
