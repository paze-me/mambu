from util import *
import base64


class AttachmentsAPI(AbstractAPI):

    url = 'documents'

    def get(self, document_id):
        """Fetches the attachment/document associated with attachment_id

        Parameters
        ----------
        document_id: int, str
            id or encodedKey for the document in mambu

        Returns
        -------
        dict
        """
        return self._get(self._postfix_url(document_id))

    def post(self, document_holder_key, document_holder_type, name,
             document_type, document_content):
        """Upload the document with content document_content

        Parameters
        ----------
        document_holder_key: str
            encodedKey for the document holder in mambu
        document_holder_type: str
            the type of document being uploaded
        name: str
            name of the document
        document_type: str
            the attachment file extension
        document_content: base64 encoded string
            The content of the document
        Returns
        -------
        dict
        """
        document = dict(
            documentHolderKey=document_holder_key, type=document_type,
            documentHolderType=document_holder_type, name=name)
        return self._post(self.url, dict(
                document=document,
                documentContent=base64.b64encode(document_content)))

    def delete(self, document_id):
        """Delete the document associated with document_id

        Parameters
        ----------
        document_id: int, str
            id or encodedkey for the document in mambu

        Returns
        -------
        dict
        """
        return self._request('delete', self._postfix_url(document_id))

    def get_by_entity(self, entity, entity_id):
        """Fetch the documents/attachments associated with the entity of type
        entity and entity_id

        Parameters
        ----------
        entity: str
            One of the standard entities e.g. clients, loans etc.
        entity_id: int, str
            id or encodedKey of the entity in mambu

        Returns
        -------
        dict
        """
        entities = ['clients', 'groups', 'savings', 'loans', 'savingsProducts',
                    'loanProducts', 'branches', 'centres', 'users']
        if entity not in entities:
            raise Exception('{} not found.  Must be one of {}'.format(
                entity, entities))
        return self._postfix_url(entity, entity_id, self.url)

    class Document:
        fields = ['documentHolderKey', 'documentHolderType', 'name', 'type']
