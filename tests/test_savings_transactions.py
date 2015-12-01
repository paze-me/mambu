import pytest


@pytest.mark.slow
def test_transactions(mambuapi):
    savings = mambuapi.get_savings(None)
    if len(savings) > 0:
        assert mambuapi.get_savings_transactions(savings[0]['id']) is not None
