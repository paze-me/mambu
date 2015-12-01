import pytest


@pytest.mark.slow
def test_savings(mambuapi):
    assert mambuapi.get_savings() != None
