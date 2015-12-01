import threading
import logging
import requests
import json
import datetime


from loans import LoansAPI
from attachments import AttachmentsAPI
from tools import datelib, data
from exception import MambuAPIException

client_metadata = data.load_yaml('clients.yaml')


class API(object):
    def __init__(self, config_):
        self.config = config_
        self.Loans = LoansAPI(self)
        self.Attachments = AttachmentsAPI(self)
        self.base_url = 'https://' + self.config.domain + '/api/'
        self.json_encoder = RequestJSONEncoder()

    def _request(self, method, url, params=None, data=None):
        headers = {'Content-Type': 'application/json'} if data else {}
        data_str = self.json_encoder.encode(data)
        logging.debug("Body: " + data_str)
        response = getattr(requests, method)(
            self.base_url + url, headers=headers, params=params, data=data_str,
            auth=(self.config.username, self.config.password))
        if response.status_code != 200 and response.status_code != 201:
            raise MambuAPIException("Error performing the request",
                                    response.status_code, response.json())
        return response.json()

    def _get(self, url, params=None, data=None):
        return self._request('get', url, params, data)

    def _post(self, url, params=None, data=None):
        return self._request('post', url, params, data)

    def _patch(self, url, params=None, data=None):
        return self._request('patch', url, params, data)

    def _delete(self, url, params=None, data=None):
        return self._request('delete', url, params, data)

    def _postfix_url(self, *args):
        return '/'.join([arg for arg in args if arg is not None])

    def get_client(self, client_id=None, params=None):
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
        return self._get(self._url_clients(client_id), params)

    def get_client_full_details(self, client_id):
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
        return self._get(self._url_clients(client_id),
                         params=dict(fullDetails=True))

    def create_client(self, client, addresses=None, custom_information=None,
                      id_documents=None):
        """Create the client with the data specified in the parameters and the
        client object

        Parameters
        ----------
        client: Client
            the client to create in mambu
        addresses: list(ClientAddress)
            list of length 1 containing an
        custom_information: list(CustomField)
            list of custom fields to set for the client
        id_documents: list(IdDocument)
            list of id documents to attach to the customer account

        Returns
        -------
        dict
        """
        return self._create_or_update_client(
            None, client, addresses, custom_information, id_documents)

    def update_client(self, client_id, client, addresses=None,
                      custom_information=None, id_documents=None):
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
        addresses: list(ClientAddress)
            list of length one containing ClientAddress data
        custom_information: list(CustomField)
            list of CustomField objects to overwrite in mambu
        id_documents: list(IdDocument)
            list of documents to attach to the customer account in mambu

        Returns
        -------
        dict
        """
        return self._create_or_update_client(
            client_id, client, addresses, custom_information, id_documents)

    def _create_or_update_client(
            self, client_id=None, client=None, addresses=None,
            custom_information=None, id_documents=None):
        """Either create or update a client in mambu

        Parameters
        ----------
        client_id: None, int, str
            id or encoded_key of client in mambu
        client: Client
            object contain the standard Client fields
        addresses: list(ClientAddress)
            list of length one containing ClientAddress data
        custom_information: list(CustomField)
            list of CustomField objects to overwrite in mambu
        id_documents: list(IdDocument)
            list of documents to attach to the customer account in mambu

        Returns
        -------
        dict
        """
        return self._post(self._url_clients(client_id), data=dict(
                client=client, idDocuments=id_documents, addresses=addresses,
                customInformation=custom_information))

    def set_client_custom_field(self, client_id, custom_field_id, value,
                                index=None):
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
        return self._patch(self._url_client_custom_field(
            client_id, custom_field_id, index),
                           data={'value': value})

    def set_client_list_custom_field(self, client_id, custom_fields):
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
                    target=self.set_client_custom_field,
                    args=(client_id, field.customFieldID, field.value)
                ) for field in custom_fields
        ]
        [t.start() for t in threads]
        [t.join() for t in threads]

    def delete_client_custom_field(self, client_id, custom_field_id,
                                   index=None):
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
        return self._delete(self._url_client_custom_field(
            client_id, custom_field_id, index))

    def update_client_addresses_field(self, client_id, addresses):
        """Updates the addresses field for client_id

        Parameters
        ----------
        client_id: int
            mambu_id for client
        addresses: dict
            the data to use to populate the addresses field

        """
        return self._post(self._url_clients(client_id),
                          data=dict(addresses=[addresses]))

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
        return self._get(self._postfix_url('customfields', custom_field_id))

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

    def get_custom_field_sets(self, _type=None):
        url = 'customfieldsets' + ('' if _type is None else '?type=%s' % _type)
        return self._get(url)

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

    def _url_clients(self, client_id=None):
        return self._postfix_url('clients', client_id)

    def _url_client_custom_field(self, client_id, custom_field_id, index=None):
        """Returns the api url for updating a custom field for a specific client

        Parameters
        ----------
        client_id
        custom_field_id
        index


        Returns
        -------

        """
        return self._postfix_url(
            self._url_clients(client_id), 'custominformation', custom_field_id,
            index)

    class Client(AbstractDataObject):
        fields = client_metadata['client']

    class GetClientParams(AbstractDataObject):
        fields = client_metadata['parameters']

    class ClientCustomField(AbstractDataObject):
        fields = client_metadata['custom_field']

    class ClientAddress(AbstractDataObject):
        fields = client_metadata['address']

    class ClientIdDocument(AbstractDataObject):
        fields = client_metadata['id_document']


class AbstractDataObject(object):
    def __init__(self, **kw):
        for key, val in kw.items():
            self.__setattr__(key, val)

    def __setattr__(self, key, val):
        if key not in type(self).fields:
            raise ValueError(key + " is not an allowed field")
        self.__dict__[key] = val

    def __getattr__(self, key):
        return self.__dict__[key]


class RequestJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, AbstractDataObject):
            return o.__dict__
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return o

