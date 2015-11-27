import pytest


@pytest.mark.slow
def test_savings(mambuapi):
    assert mambuapi.Savings.get() != None
