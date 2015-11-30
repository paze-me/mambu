import abc
from pandas.tseries.holiday import *

# helper for specifying months below
Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec = range(1, 13)

NewYearsDay = Holiday('New Years Day', month=Jan, day=1,
                      observance=weekend_to_monday)
SpringBankHoliday = Holiday('Spring Bank Holiday', month=May, day=1,
                            offset=DateOffset(weekday=MO(1)))
MayDay = Holiday('May Day', month=May, day=25, offset=DateOffset(weekday=MO(1)))
SummerBankHoliday = Holiday('August Bank', month=Aug, day=25,
                            offset=DateOffset(weekday=MO(1)))
ChristmasDay = Holiday('Christmas Day', month=Dec, day=25,
                       observance=weekend_to_monday)
BoxingDay = Holiday('Boxing Day', month=Dec, day=26,
                    observance=next_monday_or_tuesday)


class TZAbstractHolidayCalendar(AbstractHolidayCalendar):
    """Container to hold extension of holidays from AbstractHolidayCalendar so
    that it returns a tz-aware DatetimeIndex
    """

    @abc.abstractproperty
    def tz(self):
        """The timezone that will be used to make the return holidays tz-aware
        """
        pass

    def holidays(self, *args, **kwargs):
        """Extends holidays method of AbstractHolidayCalendar by localizing the
        returned DatetimeIndex

        Parameters
        ----------
        Same as AbstractHolidayCalendar

        Returns
        -------
        DatetimeIndex
            tz-aware DatetimeIndex
        """
        holidays = super(TZAbstractHolidayCalendar, self).holidays(*args, **kwargs)
        holidays = holidays.drop_duplicates()
        tz_holidays = holidays.tz_localize(self.tz)
        return tz_holidays


class UKHolidayCalendar(TZAbstractHolidayCalendar):
    """Standard UK Holidays"""
    rules = [NewYearsDay, GoodFriday, EasterMonday, SpringBankHoliday,
             MayDay, SummerBankHoliday, ChristmasDay, BoxingDay]
    tz = 'Europe/London'
