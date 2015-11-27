from util import *


class CustomFieldsAPI(AbstractAPI):
    url = 'customfields'

    def get(self, custom_field_id):
        """Get all instances of the custom field with custom_field_id

        Parameters
        ----------
        custom_field_id: int, str
            id or encoded_key of custom field in mambu

        Returns
        -------
        dict
        """
        return self._request('get', self._field_url(custom_field_id))

    def _field_url(self, custom_field_id):
        """Returns the api url for querying custom fields

        Parameters
        ----------
        custom_field_id: int, str
            id or  encoded_key for custom field in mambu

        Returns
        -------
        str
        """
        return '/'.join([self.url, custom_field_id])

    def get_sets(self, parameter_type=None):
        """Gets the in built field sets of type parameter_type

        Parameters
        ----------
        parameter_type: str
            One of (CLIENT_INFO, GROUP_INFO, LOAN_ACCOUNT_INFO,
          SAVINGS_ACCOUNT_INFO, BRANCH_INFO, CENTRE_INFO, USER_INFO)

        Returns
        -------
        dict
        """
        return self._request('get', self._field_sets_url(parameter_type))

    @staticmethod
    def _field_sets_url(parameter_type=None):
        """Gets the api url for querying inbuilt field sets

        Parameters
        ----------
        parameter_type: str
            One of (CLIENT_INFO, GROUP_INFO, LOAN_ACCOUNT_INFO,
          SAVINGS_ACCOUNT_INFO, BRANCH_INFO, CENTRE_INFO, USER_INFO)
        Returns
        -------
        str
        """
        url_ = 'customfieldsets'
        if parameter_type is not None:
            url_ += '?type=%s' % parameter_type
        return url_
