import pytest
from random import choice
import string

from mambu.tools import datelib


titles = ['Mr', 'Mrs', 'Ms', 'Prof', 'Dr', 'Eng']


@pytest.fixture(scope='function')
def password():
    """Static password meeting mambu complexity requirements"""
    return 'AComplex3Password'


@pytest.fixture(scope='function')
def user_dict(password):
    """dictionary of keys and values meeting minimum requirements to create a
    new client/user in mambu"""
    suffix = ''.join(
        choice(string.ascii_lowercase) for _ in range(8))

    return dict(
        firstName='First{}'.format(suffix),
        middleName='', lastName='Last{}'.format(suffix), birthDate='1970-11-08',
        mobilePhone1='07' + ''.join(choice(string.digits) for _ in range(9)),
        emailAddress='paze.test+{}@gmail.com'.format(suffix))


@pytest.fixture(scope='function')
def user_in_mambu(mambuapi, user_dict):
    """The dict response after creating a user with minimum fields in mambu"""
    return mambuapi.create_client(mambuapi.Client(**user_dict))


@pytest.fixture(scope='function')
def user_in_mambu_id(user_in_mambu):
    """The id for a user created in mambu"""
    return user_in_mambu['client']['id']


@pytest.fixture(scope='function')
def loan_dict(user_in_mambu):
    """Dict containing the minimum field, value pairs to create a new loan
    account in mambu for the user_in_mambu fixture"""
    client = user_in_mambu['client']
    loan = {
        "accountHolderType": "CLIENT",
        "productTypeKey": "8ae6317d50ffbb2a0151205728535505",
        "accountHolderKey": client['encodedKey'],
        "repaymentInstallments": 1,
        "loanAmount": "1200",
        "interestRate": "0",
        "repaymentPeriodCount": 1,
        "repaymentPeriodUnit": "MONTHS",
        "firstRepaymentDate": "2015-09-25T00:00:00+0000",
        "expectedDisbursementDate": "2015-09-04T00:00:00+0000",
        "tranches": [
            {"amount": "400",
             "expectedDisbursementDate": "2015-09-04T00:00:00"},
            {"amount": "400",
             "expectedDisbursementDate": "2015-09-11T00:00:00"},
            {"amount": "400",
             "expectedDisbursementDate": "2015-09-18T00:00:00"}]}
    return loan


@pytest.fixture(scope='function')
def unapproved_loan(mambuapi, loan_dict):
    """The response/loan object returned from mambu when a loan is created for
     user_in_mambu"""
    response = mambuapi.create_loan(loan_dict)['loanAccount']
    return response


@pytest.fixture(scope='function')
def approved_loan(mambuapi, unapproved_loan):
    """The loan object in mamabu for user_in_mambu once it has been approved"""
    loan_id = unapproved_loan['id']
    _approved_loan = mambuapi.approve(loan_id)
    return _approved_loan


def _shift_loan_start(_dict, start_date=None):
    start_date = datelib.datetime_today() if start_date is None \
        else datelib.coerce_datetime(start_date)
    tranches = _dict['tranches']
    disbursement_dates = map(
        lambda x: datelib.coerce_datetime(x['expectedDisbursementDate']),
        tranches)
    time_delta = start_date - disbursement_dates[0]
    new_dates = map(lambda x: datelib.mambu_datetime(x + time_delta),
                    disbursement_dates)
    for n in xrange(len(tranches)):
        tranches[n]['expectedDisbursementDate'] = new_dates[n]
    _dict['tranches'] = tranches
    for d in ['expectedMaturityDate', 'firstRepaymentDate']:
        if d in _dict:
            _dict[d] = datelib.mambu_date(
                datelib.coerce_datetime(_dict[d]) + time_delta)
    return _dict


@pytest.fixture(scope='function')
def loan_dict_today(loan_dict):
    return _shift_loan_start(loan_dict)


@pytest.fixture(scope='function')
def unapproved_loan_start_today(mambuapi, user_in_mambu, loan_dict_today):
    response = mambuapi.Loans.create(loan_dict_today)['loanAccount']
    return response


@pytest.fixture(scope='function')
def approved_loan_start_today(mambuapi, unapproved_loan_start_today):
    loan_id = unapproved_loan_start_today['id']
    mambuapi.approve(loan_id)
    response = mambuapi.get_loan(loan_id)
    return response
