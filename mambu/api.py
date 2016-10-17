import threading
import logging
import requests
import json
import datetime
import base64
import yaml
import os

from tools import datelib
from exception import MambuAPIException


with open(os.path.join(os.path.dirname(__file__), 'etc/data.yaml'), 'r') as f:
    metadata = yaml.load(f)
logger = logging.getLogger(__name__)


class RequestJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        if isinstance(o, AbstractDataObject):
            return o.__dict__
        return o


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


class API(object):
    def __init__(self, config_):
        self.config = config_
        self.base_url = 'https://{}/api/'.format(self.config.domain)
        self.json_encoder = RequestJSONEncoder()

    def _request(self, method, url, params=None, data=None):
        headers = {'Content-Type': 'application/json'} if data else {}
        data_str = self.json_encoder.encode(data)
        print self, method, self.base_url, url, params, data_str
        logging.debug("Body: " + data_str)
        response = getattr(requests, method)(
            self.base_url + url, headers=headers, params=params, data=data_str,
            auth=(self.config.username, self.config.password))
        if response.status_code != 200 and response.status_code != 201:
            try:
                message = response.json()
            except Exception:
                message = {'errorSource': response.content, 'returnCode': 950}
            raise MambuAPIException("Error performing the request",
                                    response.status_code, message)
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
        """Get the details for the client from mambu

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
        return self.get_client(client_id, params=dict(fullDetails=True))

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
        WARNING This is a post action that will overwrite any existing data for
        the client

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
        client_id: str
            if or encodedKey for client in mambu
        addresses: dict
            the data to use to populate the addresses field

        """
        return self._post(self._url_clients(client_id),
                          data=dict(addresses=[addresses]))

    def get_attachment(self, document_id):
        """Fetches the attachment/document associated with attachment_id

        Parameters
        ----------
        document_id: int, str
            id or encodedKey for the document in mambu

        Returns
        -------
        dict
        """
        return self._get(self._postfix_url('documents', document_id))

    def create_attachment(self, document_holder_key, document_holder_type, name,
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
        return self._post('documents', data=dict(
                document=document,
                documentContent=base64.b64encode(document_content)))

    def delete_attachment(self, document_id):
        """Delete the document associated with document_id

        Parameters
        ----------
        document_id: int, str
            id or encodedkey for the document in mambu

        Returns
        -------
        dict
        """
        return self._delete(self._postfix_url('documents', document_id))

    def get_attachment_by_entity(self, entity, entity_id):
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
        _entities = metadata['attachments']['entities']
        if entity not in _entities:
            raise Exception('{} not found.  Must be one of {}'.format(
                entity, _entities))
        return self._get(self._postfix_url(entity, entity_id, 'documents'))

    def get_loan(self, loan_id=None, params=None):
        """Get the loan details for the particular loan_id

        Parameters
        ----------
        loan_id: int, str
            id for the loan in mambu
        params: GetLoanParams
            params for filtering the loan

        Returns
        -------
        dict
        """
        return self._get(self._url_loans(loan_id), params)

    def get_loan_full_details(self, loan_id):
        """Get the loan details with the fullDetails parameter set to True

        Parameters
        ----------
        loan_id: str
            id or encodedKey for the loan in mambu

        Returns
        -------
        dict
        """
        return self.get_loan(loan_id, params=dict(fullDetails=True))

    def get_loans_by_entity(self, entity, entity_id, params=None):
        _entities = ['clients', 'groups']
        if entity not in _entities:
            raise Exception('{} not found.  Must be one of {}'.format(
                entity, _entities))
        return self._get(self._postfix_url(entity, entity_id, 'loans'), params)

    def get_savings(self, saving_id=None, params=None):
        return self._get(self._url_savings(saving_id), params=params)

    def get_savings_transactions(self, savings_id):
        return self._get(self._url_savings_transactions(savings_id))

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

    def create_loan(self, loan, custom_information=None):
        """Create a loan in mambu defined by the information in loan and
        custom_information

        Parameters
        ----------
        loan: dict
            data associated with the loan
        custom_information: dict
            additional custom_information for the loan

        Returns
        -------
        dict
        """
        return self._post(self._url_loans(), data=dict(
            loanAccount=loan, customInformation=custom_information))

    def update_loan(self, loan_id, loan, custom_information=None):
        """Update the loan with loan_id using details in loan and
        custom_information

        Parameters
        ----------
        loan_id: int, str
            id or encoded_key for the loan in mambu
        loan: loanAccount

        custom_information: list(customField)
            custom_information to overwrite for the loan
        Returns
        -------
        dict
        """
        return self._post(self._url_loans(loan_id), data=dict(
            loanAccount=loan, customInformation=custom_information))

    def delete_loan(self, loan_id):
        """Delete the loan with loan_id from mambu

        Parameters
        ----------
        loan_id: int, str
            id or encoded_key for the loan in mambu

        Returns
        -------
        dict
        """
        return self._delete(self._url_loans(loan_id))

    def set_loan_custom_field(self, loan_id, custom_field_id, value):
        """Set the custom field

        Parameters
        ----------
        loan_id: int, str
            id or encoded_key for the loan in mambu
        custom_field_id: str
            name or encoded_key for the custom_field
        value: object
            value to set for the custom field

        Returns
        -------
        dict
        """
        return self._patch(self._postfix_url(
            'loans', loan_id, 'custominformation', custom_field_id),
            data=dict(value=value))

    def delete_loan_custom_field(self, loan_id, custom_field_id):
        """Delete the custom field with custom_field_id from the loan with
        loan_id in mambu

        Parameters
        ----------
        loan_id: int, str
            id or encoded_key for the loan in mambu
        custom_field_id: str
            name or encoded_key for the custom field

        Returns
        -------
        dict
        """
        return self._delete(self._postfix_url(
            'loans', loan_id, 'custominformation', custom_field_id))

    def get_loans_by_single_filter(self, filter_field, filter_element=None,
                                   value=None, second_value=None):
        """Filter loans by the criteria defined in the parameters

        Parameters
        ----------
        filter_field: str
            field used to filter but in database form e.f. "LOAN_AMOUNT"
        filter_element: str
            comparison criteria for the filter_field.  Defaults to None
        value: int, str
            value to use for comparison.  Defaults to None
        second_value: int, str
            second_value to use for banded criteria such as BETWEEN.  Defaults
            to None.

        Returns
        -------
        list(Loan)
        """
        p = dict(filterSelection=filter_field, filterElement=filter_element,
                 value=value, secondValue=second_value)
        filter_constraints = [{k: v for k, v in p.iteritems() if v is not None}]
        return self.get_loans_by_filter_constraints(filter_constraints)

    def get_loans_by_filter_constraints(self, filter_constraints):
        """Use a list of filter constraints to search for loans matching the
        criteria

        Parameters
        ----------
        filter_constraints: list(dict)
            each element of the list should be a a filterConstraint with at
            least the fields filterSelection and filterElement.  value and
            value2 may be supplied depending on the filter

        Returns
        -------
        list(dict)
        """
        return self._post(self._url_loans('search'),
                          data=dict(filterConstraints=filter_constraints))

    def get_disbursements_due_on_date(self, datestr):
        result = []
        loans = self.get_loan()
        _date = datelib.coerce_date(datestr)
        for loan in loans:
            pending_tranches = [
                t for t in loan['tranches']
                if 'disbursementTransactionKey' not in t
                and datelib.coerce_date(t['expectedDisbursementDate']) == _date]
            if len(pending_tranches) == 1:
                tranche = pending_tranches[0]
                amount = float(tranche['amount'])
                result.append(dict(
                    trancheEncodedKey=tranche['encodedKey'], amount=amount,
                    loanEncodedKey=loan['encodedKey'],
                    accountHolderKey=loan['accountHolderKey'], loanId=loan['id'],
                    expectedDisbursementDate=tranche['expectedDisbursementDate']))
            elif len(pending_tranches) > 1:
                logger.warning('%s has too many tranches pending on %s' % (
                    loan['id'], datestr))
        return result

    def get_disbursements_due_today(self):
        """Return a list of loans with expectedDisbursementDate today.  Specific
        use of the more general get_loans_by_filter_field

        Returns
        -------
        list(Loan)
        """
        datestr = datelib.mambu_date(datelib.date_today())
        return self.get_disbursements_due_on_date(datestr)

    def get_disbursements_due_in_xbdays(self, days):
        due_date = datelib.mambu_date(datelib.next_n_bday(n=days))
        return self.get_disbursements_due_on_date(due_date)

    def get_principals_due_today(self):
        return self.get_loans_by_single_filter('EXPECTED_MATURITY_DATE', 'TODAY')

    def get_principals_due_on_date(self, datestr):
        datestr = datelib.mambu_date(datestr)
        return self.get_loans_by_single_filter(
            'EXPECTED_MATURITY_DATE', 'ON', datestr)

    def get_principals_due_in_xbdays(self, days):
        due_date = datelib.mambu_date(datelib.next_n_bday(n=days))
        return self.get_principals_due_on_date(due_date)

    def get_repayments_due_on_date(self, datestr):
        datestr = datelib.mambu_date(datestr)
        return self.get_loans_by_single_filter(
            'FIRST_REPAYMENT_DATE', 'ON', datestr)

    def get_repayments_due_today(self):
        return self.get_loans_by_single_filter('FIRST_REPAYMENT_DATE', 'TODAY')

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

    def disburse(self, loan_id, first_repayment_date=None):
        if first_repayment_date is not None:
            first_repayment_date = datelib.mambu_date(first_repayment_date)
        #  This spelling mistake is intentional and is present in mambu
        return self._post_loan_transaction(loan_id, dict(
            type='DISBURSMENT', firstRepaymentDate=first_repayment_date))

    def disburse_with_amount(self, loan_id, pay_amount, first_repayment_date=None):
        if first_repayment_date is not None:
            first_repayment_date = datelib.mambu_date(first_repayment_date)
        #  This spelling mistake is intentional and is present in mambu
        return self._post_loan_transaction(loan_id, dict(
            type='DISBURSMENT', amount=pay_amount,
            firstRepaymentDate=first_repayment_date))


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
        return [self.disburse(loan_id, ), self.apply_fee(loan_id, fee, date)]

    def _url_savings(self, savings_id=None):
        """Return the api url in the form:

        /api/savings/{savings_id}

        Parameters
        ----------
        savings_id: str
            Optional. Defaults to None. id or encodedKey of savings in mambu

        Returns
        -------
        str
        """
        return self._postfix_url('savings', savings_id)

    def _url_savings_custom_field(self, savings_id, custom_field_id):
        """Return the api url in the form:

        /api/savings/{savings_id}/custominformation/{custom_field_id}

        Parameters
        ----------
        savings_id: str
            id or encodedKey of savings in mambu

        Returns
        -------
        str
        """
        return self._postfix_url(
            self._url_savings(savings_id), 'custominformation', custom_field_id)

    def _url_savings_transactions(self, savings_id, transaction_id=None):
        """Return the api url in the form:

        /api/savings/{savings_id}/custominformation/{custom_field_id}

        Parameters
        ----------
        savings_id: str
            id or encodedKey of savings in mambu
        transaction_id: str
            Optional. Defaults to None. id or encodedKey of transaction in mambu

        Returns
        -------
        str
        """
        return self._postfix_url(
            'savings', savings_id, 'transactions', transaction_id)

    def _url_loan_products(self, loan_product_id=None):
        """Return the api url in the form:

        /api/loanproducts/{loan_product_id}

        Parameters
        ----------
        loan_product_id: str
            Optional. Defaults to None. id or encodedKey of savings in mambu

        Returns
        -------
        str
        """
        return self._postfix_url('loanproducts', loan_product_id)

    def _url_loans(self, loan_id=None):
        """Return the api url in the form:

        /api/loans/{loan_id}

        Parameters
        ----------
        loan_id: str
            id or encodedKey of savings in mambu

        Returns
        -------
        str
        """
        return self._postfix_url('loans', loan_id)

    def _url_loan_transactions(self, loan_id):
        """Return the api url in the form:

        /api/loans/{loan_id}/transactions/{transaction_id}

        Parameters
        ----------
        loan_id: str
            id or encodedKey of savings in mambu

        Returns
        -------
        str
        """
        return self._postfix_url(self._url_loans(loan_id), 'transactions')

    def _url_clients(self, client_id=None):
        """Return the api url in the form:

        /api/clients/{client_id}

        Parameters
        ----------
        client_id: str
            Optional.  defaults to None. id or encodedKey of savings in mambu

        Returns
        -------
        str
        """
        return self._postfix_url('clients', client_id)

    def _url_client_custom_field(self, client_id, custom_field_id, index=None):
        """Return the api url in the form:

        /api/clients/{client_id}/custominformation/{custom_field_id}/{index}

        Parameters
        ----------
        client_id: str
            id or encodedKey of savings in mambu
        custom_field_id: str
            id or encodedKey of savings in mambu
        index: int
            Optional.  defaults to None. index of the field set containing the
            customField

        Returns
        -------
        str
        """
        return self._postfix_url(
            self._url_clients(client_id), 'custominformation', custom_field_id,
            index)

    class Client(AbstractDataObject):
        fields = metadata['clients']['client']

    class GetClientParams(AbstractDataObject):
        fields = metadata['clients']['parameters']

    class ClientCustomField(AbstractDataObject):
        fields = metadata['clients']['custom_field']

    class ClientAddress(AbstractDataObject):
        fields = metadata['clients']['address']

    class ClientIdDocument(AbstractDataObject):
        fields = metadata['clients']['id_document']

    class GetLoanParams(AbstractDataObject):
        fields = metadata['loans']['parameters']

    class Loan(AbstractDataObject):
        fields = metadata['loans']['fields']

    class FilterField(AbstractDataObject):
        fields = metadata['loans']['loan_account_filter_values']
