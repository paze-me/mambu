from datetime import datetime, date

from tools import datelib


def test_next_bday():
    test_date = datetime(2015, 12, 25)
    assert datelib.next_bday(test_date) == datetime(2015, 12, 29)


def test_next_n_bday():
    test_date = datetime(2015, 12, 25)
    assert datelib.next_n_bday(test_date, 3) == datetime(2015, 12, 31)


def test_format_date():
    assert datelib.format_datetime('25-Apr-15', '%d-%m-%Y') == '25-04-2015'
    assert datelib.format_datetime(
        datetime(2015, 4, 25), '%d-%m-%Y') == '25-04-2015'


def test_contis_datetime():
    assert datelib.contis_datetime('25-Apr-15') == '20150425000000'


def test_mambu_date():
    assert datelib.mambu_date('25-Apr-15') == '2015-04-25'
    assert datelib.mambu_date('25-Apr-15 12:00') == '2015-04-25'
    assert datelib.mambu_date(date(2015, 4, 25)) == '2015-04-25'
    assert datelib.mambu_date(datetime(2015, 4, 25)) == '2015-04-25'
    assert datelib.mambu_date(datetime(2015, 4, 25, 6)) == '2015-04-25'


def test_mambu_datetime():
    assert datelib.mambu_datetime('25-Apr-15') == '2015-04-25T00:00:00'
    assert datelib.mambu_datetime('25-Apr-15 12:30') == '2015-04-25T12:30:00'
    assert datelib.mambu_datetime('25-Apr-15 12:30:45') == '2015-04-25T12:30:45'
    assert datelib.mambu_datetime('2015-04-25T12:30:45+0000'
                                  ) == '2015-04-25T12:30:45'
    assert datelib.mambu_datetime(date(2015, 4, 25)) == '2015-04-25T00:00:00'
    assert datelib.mambu_datetime(datetime(2015, 4, 25)
                                  ) == '2015-04-25T00:00:00'
    assert datelib.mambu_datetime(datetime(2015, 4, 25, 6)
                                  ) == '2015-04-25T06:00:00'
    assert datelib.mambu_datetime(datetime(2015, 4, 25, 6, 51)
                                  ) == '2015-04-25T06:51:00'
    assert datelib.mambu_datetime(datetime(2015, 4, 25, 6, 51, 23)
                                  ) == '2015-04-25T06:51:23'
