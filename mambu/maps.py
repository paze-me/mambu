def calc_tranches(frequency, salary, pay_date):
    from datetime import datetime
    from dateutil.rrule import rrule, WEEKLY, MO, TU, WE, TH, FR

    today = datetime.now()
    month_start = datetime(today.year, today.month, 1, 0, 0, 0)
    freq_map = dict(weekly=(FR, 400), daily=((MO, TU, WE, TH, FR), 80))
    week_days, fee = freq_map.get(frequency, (None, None))
    if week_days is None:
        return None
    total_tranches = rrule(
        WEEKLY, dtstart=month_start, until=pay_date, byweekday=week_days)

    tranche_dates = rrule(
        WEEKLY, dtstart=datetime.now(), until=pay_date, byweekday=week_days)
    tranche_amount = salary*100/total_tranches.count()

    tranches = map(lambda x: {"amount": float(tranche_amount-fee)/float(100),
                              "expectedDisbursementDate": x.isoformat()}, tranche_dates)
    return tranches
