import pytest


@pytest.mark.slow
def test_create_client(mambuapi, user_dict):
    create_result = mambuapi.create_client(mambuapi.Client(**user_dict))
    assert create_result['client']['firstName'] == user_dict['firstName']


@pytest.mark.slow
def test_client_by_id(mambuapi, user_in_mambu):
    client = user_in_mambu['client']
    client_id = client['id']
    client_result = mambuapi.get_client(client_id)
    exclude = ['creationDate', 'approvedDate', 'lastModifiedDate']
    fields = [k for k in client if k not in exclude]
    for k in fields:
        assert client_result[k] == client[k]


@pytest.mark.slow
def test_client_get_full_details(mambuapi, user_in_mambu_id):
    client_result = mambuapi.get_client_full_details(user_in_mambu_id)
    assert client_result['client']['id'] == user_in_mambu_id


@pytest.mark.slow
def test_client_by_first_name(mambuapi, user_in_mambu):
    client_id = user_in_mambu['client']['id']
    first_name = user_in_mambu['client']['firstName']
    client_result = mambuapi.get_client(
        params=mambuapi.GetClientParams(
            firstName=first_name))
    assert client_result[0]['id'] == client_id


@pytest.mark.slow
def test_clients(mambuapi, user_in_mambu):
    client_result = mambuapi.get_client()
    assert len(client_result) > 0


@pytest.mark.slow
def test_update_user(mambuapi, user_in_mambu):
    test_name = 'newTestFirstName'
    client = user_in_mambu['client']
    client_id = client['id']
    old_firstname = client['firstName']
    client['firstName'] = test_name
    update_result = mambuapi.update_client(client_id, client)
    assert update_result['client']['firstName'] == test_name
    updated_client = mambuapi.get_client(client_id)
    assert test_name == updated_client['firstName']
    client['firstName'] = old_firstname
    update_result = mambuapi.update_client(client_id, client)
    assert update_result['client']['firstName'] == old_firstname
    old_client = mambuapi.get_client(client_id)
    assert old_client['firstName'] == old_firstname


@pytest.mark.slow
def test_custom_value(mambuapi, user_in_mambu):
    client = user_in_mambu['client']
    client_id = client['id']
    custom_field = 'c_marital_status'
    test_value = 'test_value'
    set_result = mambuapi.set_client_custom_field(
        client_id, custom_field, test_value)
    assert set_result['returnCode'] == 0
    updated_client = mambuapi.get_client_full_details(client_id)
    updated_field = updated_client['customInformation'][0]
    assert updated_field['customFieldID'] == custom_field
    assert updated_field['value'] == test_value
    result = mambuapi.delete_client_custom_field(client_id, 'c_marital_status')
    assert result['returnCode'] == 0
    old_client = mambuapi.get_client_full_details(client_id)
    assert old_client['customInformation'] == []
