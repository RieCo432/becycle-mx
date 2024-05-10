from dateutil.relativedelta import relativedelta


def get_interval_timedelta(interval: str):
    if interval == "daily":
        return relativedelta(days=1)
    elif interval == "weekly":
        return relativedelta(weeks=1)
    elif interval == "fortnightly":
        return relativedelta(weeks=2)
    elif interval == "monthly":
        return relativedelta(months=1)
    elif interval == "quarterly":
        return relativedelta(months=3)
    elif interval == "semiyearly":
        return relativedelta(months=6)
    elif interval == "yearly":
        return relativedelta(years=1)
    else:
        return relativedelta(months=1)