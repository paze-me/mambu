import os
import pytest


@pytest.mark.slow
def test_attachments_for_client(mambuapi):
    clients = mambuapi.Clients.get(None)
    if len(clients) > 0:
        assert(mambuapi.Attachments.get_by_client(clients[0]['id']) is not None)


@pytest.mark.slow
def test_attachment_for_savings(mambuapi):
    savings = mambuapi.Savings.get()
    if len(savings) > 0:
        assert(mambuapi.Attachments.get_by_savings_id(savings[0]['id']) is not None)


@pytest.mark.slow
def test_attachments_for_loans(mambuapi):
    loans = mambuapi.Loans.get(None)
    if len(loans) > 0:
        assert(mambuapi.Attachments.getForLoan(loans[0]['id']) is not None)


@pytest.mark.slow
def test_attachments_for_user(mambuapi):
    assert(mambuapi.Attachments.getForUser(1) is not None)


@pytest.mark.skipif('CODESHIP' in os.environ, reason='Not running on Codeship')
@pytest.mark.slow
def test_create_and_delete_attachment(mambuapi):
    clients = mambuapi.Clients.get(None)
    if len(clients) > 0:
        before_create = len(mambuapi.Attachments.get_by_client(clients[0]['id']))
        document = {
            "documentHolderKey": clients[0]['encodedKey'],
            "documentHolderType": "CLIENT",
            "name": "client_information",
            "type": "txt"
        }
        content = "test"
        doc = mambuapi.Attachments.create(document, content)
        after_create = len(mambuapi.Attachments.get_by_client(clients[0]['id']))
        # Check successful creation
        assert(before_create + 1 == after_create)

        attachments = mambuapi.Attachments.get_by_client(clients[0]['id'])
        mambuapi.Attachments.delete(doc['encodedKey'])
        after_delete = len(mambuapi.Attachments.get_by_client(clients[0]['id']))
        # Check successful deletion
        assert(after_create - 1 == after_delete)
