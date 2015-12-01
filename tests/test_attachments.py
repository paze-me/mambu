import pytest


@pytest.mark.slow
def test_attachments_for_client(mambuapi, user_in_mambu_id):
    assert mambuapi.get_attachment_by_entity(
        'clients', user_in_mambu_id) is not None


@pytest.mark.slow
def test_attachment_for_savings(mambuapi):
    savings = mambuapi.get_savings()
    if len(savings) > 0:
        assert mambuapi.get_attachment_by_entity(
            'savings', savings[0]['id']) is not None


@pytest.mark.slow
def test_attachments_for_loans(mambuapi, unapproved_loan):
    assert mambuapi.get_attachment_by_entity(
        'loans', unapproved_loan['id']) is not None


@pytest.mark.slow
def test_create_and_attachment(mambuapi, user_in_mambu):
    client = user_in_mambu['client']
    client_id = client['id']
    encoded_key = client['encodedKey']
    filename = 'client_information'
    doc = mambuapi.create_attachment(
        encoded_key, 'CLIENT', filename, 'txt', 'test')
    assert doc['name'] == filename
    after_create = mambuapi.get_attachment_by_entity('clients', client_id)
    assert len(after_create) == 1
    # ToDo mambuapi does not presntly have permission to delete attachments
    # mambuapi.delete_attachment(doc['encodedKey'])
    # after_delete = mambuapi.get_attachment_by_entity('clients', client_id)
    # assert len(after_delete) == 0
