import pytest

@pytest.mark.slow
def test_transactions(mambuapi):
    savings = mambuapi.Savings.get(None)
    if len(savings)>0:
        assert mambuapi.SavingsTransactions.get(savings[0]['id']) != None
