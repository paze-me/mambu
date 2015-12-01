import pytest


@pytest.mark.slow
def test_loan_products_get(mambuapi):
    result = mambuapi.get_loan_product()
    assert result is not None
    result = mambuapi.get_loan_product('salary_advance')
    assert result is not None, 'Could not find loan product salary_advance'
    result = mambuapi.get_loan_product('8a1a2fbd4f1c1730014f27fa48602746')
    assert result is not None, \
        'Could not find loan product salary_advance by using encodedKey'


@pytest.mark.slow
def test_loan_products_get_encoded_key(mambuapi):
    loan_product_id = 'salary_advance'
    encoded_key = '8a1a2fbd4f1c1730014f27fa48602746'
    result = mambuapi.get_loan_product_encoded_key(loan_product_id)
    assert result == encoded_key
