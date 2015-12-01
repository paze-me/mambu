import os
import pytest


@pytest.mark.slow
def test_attachments_for_client(mambuapi):
    clients = mambuapi.get_client(None)
    if len(clients) > 0:
        assert(mambuapi.Attachments.get_by_client(clients[0]['id']) is not None)


@pytest.mark.slow
def test_attachment_for_savings(mambuapi):
    savings = mambuapi.get_savings()
    if len(savings) > 0:
        assert(mambuapi.Attachments.get_by_savings_id(savings[0]['id']) is not None)


@pytest.mark.slow
def test_attachments_for_loans(mambuapi):
    loans = mambuapi.get_loan(None)
    if len(loans) > 0:
        assert(mambuapi.Attachments.getForLoan(loans[0]['id']) is not None)


@pytest.mark.skipif('CODESHIP' in os.environ, reason='Not running on Codeship')
@pytest.mark.slow
def test_create_and_delete_attachment(mambuapi, user_in_mambu):
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
