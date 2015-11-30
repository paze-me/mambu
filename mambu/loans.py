import logging

from mambu.tools.data import load_yaml
from tools import datelib
from util import AbstractAPI, AbstractDataObject

loans_metadata = load_yaml('loans.yaml')
logger = logging.getLogger(__name__)


class LoansAPI(AbstractAPI):
    url = 'loans'

    def get(self, loan_id=None, params=None):
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
        if params:
            params = params.__dict__
        return self._request('get', self._loan_url(loan_id), params)

    def get_full_details(self, loan_id):
        """Get the loan details with the fullDetails parameter set to True

        Parameters
        ----------
        loan_id: str
            id or encodedKey for the loan in mambu

        Returns
        -------
        dict
        """
        return self.get(loan_id, params=self.GetLoanParams(fullDetails=True))

    def get_for_client(self, client_id=None, params=None):
        """get the loan(s) associated with the client with client_id

        Parameters
        ----------
        client_id: int, str
            if or encoded_key for client in mambu
        params: GetLoanParams
            params for filtering the loan

        Returns
        -------
        dict
        """
        if params:
            params = params.__dict__
        return self._request(
            'get', self._loan_url_for_client(client_id), params)

    def get_for_group(self, group_id=None, params=None):
        """Get loan(s) details for the group with group_id

        Parameters
        ----------
        group_id: int, str
            id or encoded_key for group in mambu
        params: GetLoanParams
            params to filter with

        Returns
        -------
        dict
        """
        if params:
            params = params.__dict__
        return self._request('get', self._loan_url_for_group(group_id), params)

    def get_transactions(self, loan_id):
        """Returns a list of transactions for the loan associated with loan_id

        Parameters
        ----------
        loan_id: str
            id or encodedKey for the loan in mambu

        Returns
        -------
        list
        """
        return self._request('get', self._loan_transactions_url(loan_id))

    def create(self, loan, custom_information=None):
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
        return self._create_or_update(
            loan=loan, custom_information=custom_information)

    def update(self, loan_id, loan, custom_information=None):
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
        return self._create_or_update(loan_id, loan, custom_information)

    def delete(self, loan_id):
        """Delete the loan with loan_id from mambu

        Parameters
        ----------
        loan_id: int, str
            id or encoded_key for the loan in mambu

        Returns
        -------
        dict
        """
        return self._request('delete', self._loan_url(loan_id))

    def set_custom_field(self, loan_id, custom_field_id, value):
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
        return self._request(
            'patch', self._custom_field_url(loan_id, custom_field_id),
            data={'value': value})

    def delete_custom_field(self, loan_id, custom_field_id):
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
        return self._request(
            'delete', self._custom_field_url(loan_id, custom_field_id))

    def _create_or_update(self, loan_id=None, loan=None,
                          custom_information=None):
        """Create or update the loan with loan_id in mambu with the information
        passed in loan and custom_information

        Parameters
        ----------
        loan_id: int, str
            id or encoded_key for the loan in mambu
        loan: dict
            loan details to overwrite
        custom_information: dict
            custom_information to overwrite

        Returns
        -------
        dict
        """
        return self._request(
            'post', self._loan_url(loan_id),
            data={'loanAccount': loan, 'customInformation': custom_information})

    def _loan_url(self, loan_id=None):
        """Returns the loan_api url for amending the loan defined by loan_id

        Parameters
        ----------
        loan_id: int, str
            id or encoded_key for the loan in mambu

        Returns
        -------
        str
        """
        url_ = self.url
        if loan_id is not None:
            url_ += '/' + str(loan_id)
        return url_

    def _loan_url_for_client(self, client_id):
        """Return the api url for making changes to loans for the client defined
        by client_id

        Parameters
        ----------
        client_id: int, str
            id or encoded_key for the client in mambu

        Returns
        -------
        str
        """
        url_ = self.url
        if client_id is not None:
            url_ = '/'.join(['clients', client_id, url_])
        return url_

    def _loan_url_for_group(self, group_id):
        """Return the api url for amending loans for the group defined by
        group_id

        Parameters
        ----------
        group_id: int, str
            id or encoded_key for the group in mambu

        Returns
        -------
        str
        """
        url_ = self.url
        if group_id is not None:
            url_ = '/'.join(['groups', group_id, url_])
        return url_

    def _loan_transactions_url(self, loan_id):
        url_ = '/'.join([self.url, loan_id, 'transactions'])
        return url_

    def _custom_field_url(self, loan_id, custom_field_id):
        """Return the api_url for amending the custom field for the loan defined
        by loan_id

        Parameters
        ----------
        loan_id: int, str
            id or encoded_key for the loan in mambu
        custom_field_id: str
            id or encoded_key for the custom_field i mambu

        Returns
        -------
        dict
        """
        return '/'.join([self._loan_url(loan_id), 'custominformation',
                         custom_field_id])

    def _loan_filter_field_url(self):
        """Return the url for performing filters on loans

        Returns
        -------
        str
        """
        return '/'.join([self.url, 'search'])

    def get_loans_by_filter_field(self, filter_field, filter_element=None,
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
        filter_constraints = {k: v for k, v in p.iteritems() if v is not None}
        return self._request(
            'post', self._loan_filter_field_url(),
            data=dict(filterConstraints=[filter_constraints]))

    def get_disbursements_due_today(self):
        """Return a list of loans with expectedDisbursementDate today.  Specific
        use of the more general get_loans_by_filter_field

        Returns
        -------
        list(Loan)
        """
        datestr = datelib.mambu_date(datelib.date_today())
        return self.get_disbursements_due_on_date(datestr)

    def get_disbursements_due_on_date(self, datestr):
        result = []
        loans = self.get()
        _date = datelib.coerce_date(datestr)
        for loan in loans:
            pending_tranches = [t for t in loan['tranches']
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

    def get_disbursements_due_in_xbdays(self, days):
        due_date = datelib.mambu_date(datelib.next_n_bday(n=days))
        return self.get_disbursements_due_on_date(due_date)

    def get_principals_due_today(self):
        return self.get_loans_by_filter_field('EXPECTED_MATURITY_DATE', 'TODAY')

    def get_principals_due_on_date(self, datestr):
        datestr = datelib.mambu_date(datestr)
        return self.get_loans_by_filter_field(
            'EXPECTED_MATURITY_DATE', 'ON', datestr)

    def get_principals_due_in_xbdays(self, days):
        due_date = datelib.mambu_date(datelib.next_n_bday(n=days))
        return self.get_principals_due_on_date(due_date)

    def get_repayments_due_on_date(self, datestr):
        datestr = datelib.mambu_date(datestr)
        return self.get_loans_by_filter_field('FIRST_REPAYMENT_DATE', 'ON', datestr)

    def get_repayments_due_today(self):
        return self.get_loans_by_filter_field('FIRST_REPAYMENT_DATE', 'TODAY')

    class GetLoanParams(AbstractDataObject):
        fields = loans_metadata['parameters']

    class Loan(AbstractDataObject):
        fields = loans_metadata['fields']

    class FilterField(AbstractDataObject):
        fields = loans_metadata['loan_account_filter_values']
