import datetime

from dateutil import parser
from pandas.tseries.offsets import CustomBusinessDay

from .calendars import UKHolidayCalendar


def date_today():
    """Shortcut function for datetime.datetime.today().date()

    Returns
    -------
    datetime.date
        The datetime.date for today
    """
    return datetime.datetime.today().date()


def datetime_today():
    """Shortcut function to return a today's date as a datetime at midnight
    If the datetime now is 25-Apr-15 11:22 this will return
    datetime.datetime(2015, 4, 25, 11, 22)

    Returns
    -------
    datetime.datetime
        The datetime.datetime for midnight today i.e. in the past
    """
    return datetime.datetime.combine(date_today(), datetime.time(0))


def next_n_bday(start_date=None, n=1):
    if start_date is None:
        start_date = date_today()
    return start_date + CustomBusinessDay(calendar=UKHolidayCalendar(), n=n)


def next_bday(start_date=None):
    return next_n_bday(start_date, 1)


def coerce_date(candidate, dayfirst=False):
    result = coerce_datetime(candidate, dayfirst=dayfirst)
    try:
        result = result.date()
    except AttributeError:
        result = None
    return result


def coerce_datetime(candidate, dayfirst=False):
    """Coerce the candidate into a datetime.datetime if possible

    Parameters
    ----------
    candidate: str, datetime.date, datetime.datetime
        The candidate to be coerced into a datetime.datetime or datetime.date
    dayfirst: bool
        If the candidate is a str then assume European style date format if
        True or American if False

    Returns
    -------
    datetime.datetime, datetime.date
    """
    if candidate is None:
        result = None
    elif isinstance(candidate, datetime.datetime):
        result = candidate
    elif isinstance(candidate, datetime.date):
        result = datetime.datetime.combine(candidate, datetime.time(0))
    else:
        try:
            result = parser.parse(candidate, dayfirst=dayfirst)
        except ValueError:
            raise ValueError(
                'Could not coerce datetime from candidate %s' % candidate)
    return result


def format_datetime(datetime_candidate, format_str):
    """Coerce the candidate_datetime before applying the specified format

    Parameters
    ----------
    datetime_candidate: str, datetime.date, datetime.datetime
        candidate to be formatted
    format_str: str
        string specifying format of date e.g. '%d-%m-%y'

    Returns
    -------
    str
    """
    result = coerce_datetime(datetime_candidate)
    try :
        result = result.strftime(format_str)
    except AttributeError:
        result = None
    return result


def contis_datetime(datetime_candidate):
    """Given a candidate date, coerce into a date if possible and then return a
    string in the format expected by the contis api

    Format for date field must be "YYYYMMDDHHmmss (24 hour time format) used to
    generate hash. e.g. "17/06/2012 03:45:36 PM" should be used as
    "20120617154536"

    Parameters
    ----------
    datetime_candidate: str, datetime.date, datetime.datetime
        The date to attempt to coerce and format

    Returns
    -------
    str
    """
    return format_datetime(datetime_candidate, '%Y%m%d%H%M%S')


def mambu_date(date_candidate):
    """Given a candidate date, coerce into a date if possible and then return a
    string in format expected by the mambu api

    Can have date format yyyy-MM-dd

    Parameters
    ----------
    date_candidate: str, datetime.date, datetime.datetime
        the candidate date for formatting

    Returns
    -------
    str
    """
    return format_datetime(date_candidate, '%Y-%m-%d')


def mambu_datetime(datetime_candidate):
    """Given a candidate date or datetime, coerce into a datetime

    Can have datetime format yyyy-MM-dd'T'HH:mm:ss

    Parameters
    ----------
    datetime_candidate: str, datetime.date, datetime.datetime
        candidate for formatting

    Returns
    -------
    str
    """
    return format_datetime(datetime_candidate, '%Y-%m-%dT%H:%M:%S')
