from util import *


class SavingsAPI(AbstractAPI):
    url = 'savings'

    def get(self, savings_id=None, params=None):
        """Get the data associated with the savings object defined by savings_id

        Parameters
        ----------
        savings_id: int, str
            id or encoded_key of savings in mambu
        params: dict
            parameters to use to filter savings accounts

        Returns
        -------
        dict
        """
        if params:
            params = params.__dict__
        return self._request('get', self._savings_url(savings_id), params)

    def create(self, savings_account, custom_information=None):
        """Create a savings account from the data in savings_account and
        custom_information

        Parameters
        ----------
        savings_account: SavingsAccount
            data associated with a savings account
        custom_information: list(CustomField)
            additional custom defined data associated with a savings account

        Returns
        -------
        dict
        """
        return self._create_or_update(savings_account=savings_account,
                                      custom_information=custom_information)

    def update(self, savings_id, savings_account, custom_information=None):
        """Update the data in savings account with savings_id with the data
        provided in savings_account and custom_information.
        WARNING this is a POST protocol that will overwrite all custom fields
        presently associated with savings_id

        Parameters
        ----------
        savings_id: int, str
            id or encoded_key for savings account
        savings_account: SavingsAccount
            data associated with the savings account
        custom_information: list(CustomField)
            custom_information to write to savings_id
        Returns
        -------
        dict
        """
        return self._create_or_update(
            savings_id, savings_account, custom_information)

    def set_custom_field(self, savings_id, custom_field_id, value):
        """Set the customField with custom_filed_id in the savings account with
        savings_id in mambu to the data passed in value

        Parameters
        ----------
        savings_id: int, str
            id or encoded_key for the savings account in mambu
        custom_field_id: str
            name or encoded key for the custom_field in mambu
        value: object
            value to set for the custom field associated with savings_id
        Returns
        -------
        dict
        """
        return self._request('patch', self._custom_field_url(
            savings_id, custom_field_id), data={'value': value})

    def delete_custom_field(self, savings_id, custom_field_id):
        """Delete the custom field defined by custom_field_id from the savings
        account with savings_id

        Parameters
        ----------
        savings_id: int, str
            id or encoded_key for the savings account in mambu
        custom_field_id: str
            name or encoded key for the custom_field in mambu
        Returns
        -------
        dict
        """
        return self._request(
            'delete', self._custom_field_url(savings_id, custom_field_id))

    def _savings_url(self, savings_id=None):
        """Return the api url for amending the savings account with savings_id

        Parameters
        ----------
        savings_id: int, str
            id or encoded_key for the savings account in mambu

        Returns
        -------
        dict
        """
        url_ = self.url
        if savings_id is not None:
            url_ += '/' + str(savings_id)
        return url_

    def _create_or_update(self, savings_id=None, savings_account=None,
                          custom_information=None):
        """Create or update the data associated with savings_id

        Parameters
        ----------
        savings_id: int, str
            id or encoded_key for the savings account in mambu
        savings_account: SavingsAccount
            data defining the savings account
        custom_information: list(CustomField)
            custom_information for teh savings account

        Returns
        -------
        dict
        """
        return self._request('post', self._savings_url(savings_id),
                             data={'savingsAccount': savings_account,
                                   'customInformation': custom_information})

    def _custom_field_url(self, savings_id, custom_field_id):
        """Return the api url for amending the custom field with custom_filed_id
        for the savings account with savings_id

        Parameters
        ----------
        savings_id: int, str
            id or encoded_key for the savings account in mambu
        custom_field_id: str
            name or encoded_key for the custom field in mambu

        Returns
        -------
        dict
        """
        return '%s/custominformation/%s' % (self._savings_url(savings_id),
                                            custom_field_id)

    class GetSavingParams(AbstractDataObject):
        fields = ['branchId', 'centreId', 'creditOfficerUsername',
                  'accountState', 'fullDetails', 'offset', 'limit']

    class SavingsAccount(AbstractDataObject):
        fields = [
            'encodedKey', 'id', 'accountHolderType', 'accountHolderKey',
            'productTypeKey', 'name', 'accountType', 'accountState', 'balance',
            'accruedInterest', 'maturityDate', 'targetAmount',
            'recommendedDepositAmount', 'maxWidthdrawlAmount', 'targetAmount',
            'lockedBalance', 'overdrafAmount', 'overdraftInterestAccrued',
            'overdraftExpiryDate', 'overdraftLimit', 'allowOverdraft',
            'assignedBranchKey', 'assignedCentreKey', 'interestPaymentPoint',
            'interestPaymentDates', 'withholdingTaxSourceKey',
            'overdraftInterestRateSource', 'overdraftInterestRate',
            'overdraftInterestRateReviewCount',
            'overdraftInterestRateReviewUnit', 'notes']

    class CustomField(AbstractDataObject):
        fields = ['customFieldID', 'value']
