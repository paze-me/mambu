import threading

from mambu.tools.data import load_yaml
from util import *

client_metadata = load_yaml('clients.yaml')


class ClientsAPI(AbstractAPI):
    url = 'clients'
    get_params = frozenset(client_metadata['parameters'])
    _c_addresses_map = dict(
        c_address1='line1', c_address2='line2', c_city='city',
        c_country='country', c_post_code='postcode')

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
        return self._request('get', self._client_url(client_id), params)

    def get_full_details(self, client_id):
        """Get the full details for the client associated with client_id by
        setting fullDetails=True in parameters

        Parameters
        ----------
        client_id: int, str
            if or encodedKey for client in mambu

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
        return self._request(
            'post', self._client_url(client_id), data={
                'client': client, 'idDocuments': id_documents,
                'addresses': addresses,
                'customInformation': custom_information})

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
        return self._request(
            'patch', self._custom_field_url(client_id, custom_field_id, index),
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
        return self._request(
            'delete', self._custom_field_url(client_id, custom_field_id, index))

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

    def max_field_index(self, client_id, custom_field_ids):
        """Returns the maximum of customFieldSetGroupIndex for the
        custom_field_id.  If the custom field does not yet exist or is not in a
        field set then -1 is returned

        Parameters
        ----------
        client_id: int, str
            id or encoded_key for teh client in mambu
        custom_field_ids: str, list
            customFieldID or list of customFieldIDs to use for filter

        Returns
        -------
        int
        """
        if not isinstance(custom_field_ids, list):
            custom_field_ids = [custom_field_ids]
        max_index = -1
        client = self.get(client_id,
                          params=self.GetClientParams(fullDetails=True))
        for field in client['customInformation']:
            if field['customFieldID'] in custom_field_ids:
                max_index = max(field['customFieldSetGroupIndex'], max_index)
        return max_index

    def create_address_details(self, client_id, data):
        """Create a new address details field set populated with data from data
        parameter

        Parameters
        ----------
        client_id: int
            mambu client id
        data: dict
            The field names and value to use in the new address details field
            set

        """
        new_index = self.max_field_index(
            client_id, self._c_addresses_map.keys()) + 1
        index = -1
        for customFieldID, value in data.iteritems():
            self.set_custom_field(client_id, customFieldID, value, index)
            index = new_index

    def update_addresses_field(self, client_id, addresses):
        """Updates the addresses field for client_id

        Parameters
        ----------
        client_id: int
            mambu_id for client
        addresses: dict
            the data to use to populate the addresses field

        """
        return self._request('post', self._client_url(client_id),
                             data=dict(addresses=[addresses]))

    def map_custom_to_addresses(self, custom_data):
        return {self._c_addresses_map[k]: v for k, v in custom_data.iteritems()
                if k in self._c_addresses_map}

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

    def client_from_user_profile(self, user, profile):
        client = self.Client(
            firstName=user.firstname, middleName=user.middlename,
            lastName=user.lastname, emailAddress=user.email,
            birthDate=profile.dob.strftime('%Y-%m-%d'),
            mobilePhone1=profile.mobile)
        return client

    def addresses_from_be_address(self, address):
        result = self.Address(
            line1=address.address_line_1, line2=address.address_line_2,
            city=address.city, postcode=address.postcode)
        return [result]

    def custom_address_from_be_address(self, address, index=-1):
        line1 = self.CustomField(
            customFieldID='c_address1', value=address.address_line_1,
            customFieldSetGroupIndex=index)
        line2 = self.CustomField(
            customFieldID='c_address2', value=address.address_line_2,
            customFieldSetGroupIndex=index)
        city = self.CustomField(
            customFieldID='c_city', value=address.city,
            customFieldSetGroupIndex=index)
        postcode = self.CustomField(
            customFieldID='c_post_code', value=address.postcode,
            customFieldSetGroupIndex=index)
        time_lived = self.CustomField(
            customFieldID='c_years_in_address',
            value=address.time_lived_here,
            customFieldSetGroupIndex=index)
        return [line1, line2, city, postcode, time_lived]

    def custominfo_from_client_data(self, data):
        marital_status = self.CustomField(
            customFieldID='c_marital_status', value=data.marital)
        dependents = self.CustomField(
            customFieldID='c_number_of_dependents', value=data.dependants)
        custominfo = [marital_status, dependents]
        # ToDo Where is building_name being set/stored?
        for index, address in enumerate(data.addresses[1:]):
            custominfo.extend(
                self.custom_address_from_be_address(address, index))
        return custominfo

    def custominfo_from_employment_profile_data(self, data):
        # ToDo Where is building_name being set/stored?
        company_name = self.CustomField(
            customFieldID='company_name', value=data.employer_name)
        address_1 = self.CustomField(
            customFieldID='company_address_1', value=data.address_line_1)
        address_2 = self.CustomField(
            customFieldID='company_address_2', value=data.address_line_2)
        city = self.CustomField(
            customFieldID='company_city', value=data.city)
        postcode = self.CustomField(
            customFieldID='company_post_code', value=data.company_post)
        employment_length = self.CustomField(
            customFieldID='years_with_company', value=data.time_with_employer)
        employment_status = self.CustomField(
            customFieldID='c_employment_status', value=data.employment_status)
        employer_status = self.CustomField(
            customFieldID='employment_status_with_company', value='Current')
        salary = self.CustomField(
            customFieldID='c_net_salary', value=data.net_salary)
        pay_day = self.CustomField(
            customFieldID='c_specific_payday',
            value=data.pay_date.strftime('%d'))
        pay_month = self.CustomField(
            customFieldID='c_monthly_payday',
            value=data.pay_date.strftime('%m'))
        pay_freq = self.CustomField(
            customFieldID='c_income_frequency', value=data.income_freq)
        custominfo = [company_name, address_1, address_2, city, postcode,
                      employment_length, employment_status, employer_status,
                      salary, pay_day, pay_month, pay_freq]
        return custominfo

    def loan_from_user(self, user, tranches):
        # ToDo hardcoded for now as I'm not sure the best way to get the key from mambu
        productTypeKey = u'8a1a2fbd4f1c1730014f27fa48602746'
        loan = dict(
            accountHolderType="CLIENT", productTypeKey=productTypeKey,
            accountHolderKey=user.encodedkey, repaymentInstallments=1,
            loanAmount=user.employmentprofile.net_salary, interestRate="0",
            repaymentPeriodCount=1, repaymentPeriodUnit="MONTHS",
            tranches=tranches)
        return loan
