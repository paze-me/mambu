from datetime import datetime

from pandas.tseries.offsets import CustomBusinessDay

from tools import calendars


def test_UKHolidayCalendar():
    uk_calendar = calendars.UKHolidayCalendar
    base_day = datetime(2015, 12, 25)
    bday_uk1 = base_day + CustomBusinessDay(calendar=uk_calendar())
    assert(bday_uk1 == datetime(2015, 12, 29))
    bday_uk3 = base_day + CustomBusinessDay(calendar=uk_calendar(), n=3)
    assert(bday_uk3 == datetime(2015, 12, 31))
    bday_uk4 = base_day + CustomBusinessDay(calendar=uk_calendar(), n=4)
    assert(bday_uk4 == datetime(2016, 1, 4))
