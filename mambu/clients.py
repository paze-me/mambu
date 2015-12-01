import threading

from mambu.tools.data import load_yaml
from util import *


client_metadata = load_yaml('clients.yaml')


class ClientsAPI(AbstractAPI):
    url = 'clients'
    get_params = frozenset(client_metadata['parameters'])

    def get(self, client_id=None, params=None):
        """Get the details for the client fro mambu

        Parameters
        ----------
        client_id: int, str
            id or encoded_key for the client in mambu
        params:
            parameters to use for filtering
        Returns
        -------
        dict
        """
        if params:
            params = params.__dict__
        return self._get(self._client_url(client_id), params)

    def get_full_details(self, client_id):
        """Get the full details for the client associated with client_id by
        setting fullDetails=True in parameters

        Parameters
        ----------
        client_id: int, str
            if or encodedKey for client in nginxmambu

        Returns
        -------
        dict
        """
        return self.get(
            client_id, params=self.GetClientParams(fullDetails=True))

    def create(self, client, addresses=None, custom_information=None,
               id_documents=None):
        """Create the client with the data specified in the parameters and the
        client object

        Parameters
        ----------
        client: Client
            the client to create in mambu
        addresses: list(self.Address)
            list of length 1 containing an
        custom_information: list(CustomField)
            list of custom fields to set for the client
        id_documents: list(IdDocument)
            list of id documents to attach to the customer account

        Returns
        -------
        dict
        """
        return self._create_or_update(
            None, client, addresses, custom_information, id_documents)

    def update(self, client_id, client, addresses=None, custom_information=None,
               id_documents=None):
        """Update the client in mambu with client_id using the data provided in
        the parameters
        WARNING This is a post action that will overwrite and existing data for
        teh client

        Parameters
        ----------
        client_id: int, str
            id or encoded_key of client in mambu
        client: Client
            object contain the standard Client fields
        addresses: list(Address)
            list of length one containing Address data
        custom_information: list(CustomField)
            list of CustomField objects to overwrite in mambu
        id_documents: list(IdDocument)
            list of documents to attach to the customer account in mambu

        Returns
        -------
        dict
        """
        return self._create_or_update(
            client_id, client, addresses, custom_information, id_documents)

    def _create_or_update(self, client_id=None, client=None, addresses=None,
                          custom_information=None, id_documents=None):
        """Either create or update a client in mambu

        Parameters
        ----------
        client_id: None, int, str
            id or encoded_key of client in mambu
        client: Client
            object contain the standard Client fields
        addresses: list(Address)
            list of length one containing Address data
        custom_information: list(CustomField)
            list of CustomField objects to overwrite in mambu
        id_documents: list(IdDocument)
            list of documents to attach to the customer account in mambu

        Returns
        -------
        dict
        """
        return self._post(self._client_url(client_id), data=dict(
                client=client, idDocuments=id_documents, addresses=addresses,
                customInformation=custom_information))

    def _client_url(self, client_id=None):
        """Returns the api url for updating a specific client in mambu

        Parameters
        ----------
        client_id: int, str
            id or encoded_key of client in mambu

        Returns
        -------
        str
        """
        url_ = self.url
        if client_id is not None:
            url_ += '/%s' % client_id
        return url_

    def set_custom_field(self, client_id, custom_field_id, value, index=None):
        """Sets the value of the customFieldId specified.  If the customFieldId
        is within a fieldset then index must be set to customFieldSetGroupIndex

        In order to create a new customfield associated with a field set index
        must be set to -1

        Parameters
        ----------
        client_id: int, str
            id or encoded_key for the client in mambu
        custom_field_id: str
            name or encoded_key of the custom field
        value:
            value to use to update the custom field
        index
            Defaults to None.  customFieldSetGroupIndex of the field set
            containing the custom field.  Setting index = -1 will create a new
            field set containing the customfield

        Returns
        -------
        json
        """
        return self._patch(self._custom_field_url(client_id, custom_field_id,
                                                  index),
                           data={'value': value})

    def set_list_custom_field(self, client_id, custom_fields):
        """Iterate through the custom_fields specified in custom_fields and call
        set_custom_field on each one

        Parameters
        ----------
        client_id: int, str
            id or encoded_key of client in mambu
        custom_fields: list
            list of CustomField objects to process

        Returns
        -------

        """
        threads = [
                threading.Thread(
                    target=self.set_custom_field,
                    args=(client_id, field.customFieldID, field.value)
                ) for field in custom_fields
        ]
        [t.start() for t in threads]
        [t.join() for t in threads]

    def delete_custom_field(self, client_id, custom_field_id, index=None):
        """Deletes the customFieldId specified.  If the customFieldId is within
        a fieldset then index must be set to customFieldSetGroupIndex

        Parameters
        ----------
        client_id: int, str
            id or encoded_key for the client in mambu
        custom_field_id: str
            name or encoded_key of the custom field being deleted
        index
            defaults to None.  customFieldSetGroupIndex of the field set
            containing the custom field

        Returns
        -------
        dict
        """
        return self._delete(self._custom_field_url(client_id, custom_field_id,
                                                   index))

    def _custom_field_url(self, client_id, custom_field_id, index=None):
        """Returns the api url for updating a custom field for a specific client

        Parameters
        ----------
        client_id
        custom_field_id
        index


        Returns
        -------

        """
        url = '/'.join([self._client_url(client_id), 'custominformation',
                        custom_field_id])
        if index is not None:
            url += '/%s' % index
        return url

    def update_addresses_field(self, client_id, addresses):
        """Updates the addresses field for client_id

        Parameters
        ----------
        client_id: int
            mambu_id for client
        addresses: dict
            the data to use to populate the addresses field

        """
        return self._post(self._client_url(client_id),
                          data=dict(addresses=[addresses]))

    class GetClientParams(AbstractDataObject):
        fields = client_metadata['parameters']

    class Client(AbstractDataObject):
        fields = client_metadata['client']

    class CustomField(AbstractDataObject):
        fields = client_metadata['custom_field']

    class Address(AbstractDataObject):
        fields = client_metadata['address']

    class IdDocument(AbstractDataObject):
        fields = client_metadata['id_document']
