import pytest


@pytest.mark.slow
def test_get_custom_field(mambuapi):
    custom_field = 'c_marital_status'
    result = mambuapi.get_custom_field(custom_field)
    assert custom_field == result['id']


@pytest.mark.slow
def test_get_custom_field_sets(mambuapi):
    result = mambuapi.get_custom_field_sets('CLIENT_INFO')
    assert isinstance(result, list)
