import pytest


@pytest.mark.slow
def test_client_by_id(mambuapi, user_in_mambu_id):
    client_result = mambuapi.Clients.get(user_in_mambu_id)
    assert client_result is not None


@pytest.mark.slow
def test_client_by_first_name(mambuapi, user_in_mambu_id):
    client = mambuapi.Clients.get(user_in_mambu_id)
    first_name = client['firstName']
    assert mambuapi.Clients.get(
        params=mambuapi.Clients.GetClientParams(
            firstName=first_name)
    )[0]['emailAddress'] == client['emailAddress']


@pytest.mark.slow
def test_clients(mambuapi):
    assert mambuapi.Clients.get(
        None, mambuapi.Clients.GetClientParams(fullDetails=True)) is not None


@pytest.mark.slow
def test_client(mambuapi):
    clients = mambuapi.Clients.get(None)
    if len(clients) > 0:
        assert mambuapi.Clients.get(clients[0]['id']) is not None


@pytest.mark.slow
def test_update_user(mambuapi, user_in_mambu_id):
    test_name = 'newTestFirstName'
    client = mambuapi.Clients.get(user_in_mambu_id)
    old_firstname = client['firstName']
    client['firstName'] = test_name
    update_result = mambuapi.Clients.update(user_in_mambu_id, client)
    assert update_result['client']['firstName'] == test_name
    updated_client = mambuapi.Clients.get(user_in_mambu_id)
    assert test_name == updated_client['firstName']
    client['firstName'] = old_firstname
    update_result = mambuapi.Clients.update(user_in_mambu_id, client)
    assert update_result['client']['firstName'] == old_firstname
    old_client = mambuapi.Clients.get(user_in_mambu_id)
    assert old_client['firstName'] == old_firstname


@pytest.mark.slow
def test_custom_value(mambuapi, user_in_mambu):
    client = user_in_mambu['client']
    client_id = client['id']
    custom_field = 'c_marital_status'
    test_value = 'test_value'
    set_result = mambuapi.Clients.set_custom_field(
        client_id, custom_field, test_value)
    assert set_result['returnCode'] == 0
    updated_client = mambuapi.Clients.get_full_details(client_id)
    updated_field = updated_client['customInformation'][0]
    assert updated_field['customFieldID'] == custom_field
    assert updated_field['value'] == test_value
    result = mambuapi.Clients.delete_custom_field(client_id, 'c_marital_status')
    assert result['returnCode'] == 0
    old_client = mambuapi.Clients.get_full_details(client_id)
    assert old_client['customInformation'] == []


@pytest.mark.slow
def test_get_customField(mambuapi):
    assert mambuapi.CustomFields.get('c_marital_status') is not None


@pytest.mark.slow
def test_get_customFieldSets(mambuapi):
    assert mambuapi.CustomFields.get_sets('CLIENT_INFO') is not None
