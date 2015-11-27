import pytest


@pytest.mark.slow
def test_client_by_id(mambuapi, user_in_mambu):
    assert mambuapi.Clients.get(user_in_mambu.mambuid) != None


@pytest.mark.slow
def test_client_by_first_name(mambuapi, user_in_mambu):
    assert mambuapi.Clients.get(
        params=mambuapi.Clients.GetClientParams(
            firstName=user_in_mambu.firstname)
    )[0]['emailAddress'] == user_in_mambu.email


@pytest.mark.slow
def test_client_update_fieldset_customfield(mambuapi, user_in_mambu):
    mambuapi.Clients.set_custom_field(
        user_in_mambu.mambuid, 'c_city', 'London Town', -1)


@pytest.mark.slow
def test_create_new_client_fieldset_customfield(mambuapi, user_in_mambu):
    """Checks that a new customfield is created within a field set
    then deletes the new field (and associated field set)
    """
    customfield = 'c_city'

    max_index_before = mambuapi.Clients.max_field_index(
        user_in_mambu.mambuid, customfield)
    mambuapi.Clients.set_custom_field(
        user_in_mambu.mambuid, customfield, 'London Town', -1)
    max_index_after = mambuapi.Clients.max_field_index(
        user_in_mambu.mambuid, customfield)
    assert max_index_before + 1 == max_index_after
    mambuapi.Clients.delete_custom_field(
        user_in_mambu.mambuid, customfield, max_index_after)


@pytest.mark.slow
def test_create_address_details(mambuapi, user_in_mambu):
    """Checks creating a new address details set and then populating"""
    test_data = dict(c_address1='1 test', c_city='test city',
                     c_post_code='aa1 1aa', c_years_in_address=1)
    mambuapi.Clients.create_address_details(user_in_mambu.mambuid, test_data)
    max_index = mambuapi.Clients.max_field_index(user_in_mambu.mambuid, 'c_city')
    for field in test_data:
        mambuapi.Clients.delete_custom_field(user_in_mambu.mambuid, field, max_index)


@pytest.mark.slow
def test_update_addresses_field(mambuapi, user_in_mambu):
    """Rip out the addresses field associated with user_in_mambu.mambuid and check
    that it updates with new details.  Return the addresses field to the
    original at the end
    """
    old_addresses = mambuapi.Clients.get(
        user_in_mambu.mambuid,
        params=mambuapi.Clients.GetClientParams(fullDetails=True))['addresses'][0]
    data = dict(c_address1='1 test', c_post_code='aa1 1aa')
    addresses = mambuapi.Clients.map_custom_to_addresses(data)

    mambuapi.Clients.update_addresses_field(user_in_mambu.mambuid, addresses)

    new_addresses = mambuapi.Clients.get(
        user_in_mambu.mambuid,
        params=mambuapi.Clients.GetClientParams(fullDetails=True))['addresses'][0]

    assert old_addresses['line1'] != new_addresses['line1']
    assert old_addresses['postcode'] != new_addresses['postcode']
    assert 'city' not in new_addresses
    assert 'city' in old_addresses


@pytest.mark.slow
def test_clients(mambuapi):
    assert mambuapi.Clients.get(
        None,
        mambuapi.Clients.GetClientParams(fullDetails=True)
    ) != None


@pytest.mark.slow
def test_client(mambuapi):
    clients = mambuapi.Clients.get(None)
    if len(clients) > 0:
        assert mambuapi.Clients.get(clients[0]['id']) != None


@pytest.mark.slow
def test_update_user(mambuapi):
    clients = mambuapi.Clients.get(None)
    updated_client = clients[0]
    updated_client['firstName'] = 'newGarry'
    mambuapi.Clients.update(updated_client['id'], updated_client)
    last_client = mambuapi.Clients.get(updated_client['id'])
    assert 'newGarry' ==  last_client['firstName']


@pytest.mark.slow
def test_custom_value(mambuapi):
    clients = mambuapi.Clients.get(None)
    if len(clients) > 0:
        mambuapi.Clients.set_custom_field(clients[0]['id'], 'c_marital_status', 'test_value')
        mambuapi.Clients.delete_custom_field(clients[0]['id'], 'c_marital_status')


@pytest.mark.slow
def test_get_customField(mambuapi):
    assert mambuapi.CustomFields.get('c_marital_status') != None

@pytest.mark.slow
def test_get_customFieldSets(mambuapi):
    assert mambuapi.CustomFields.get_sets('CLIENT_INFO') != None
