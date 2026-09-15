from dateutil.relativedelta import relativedelta
from datetime import date


def number_of_days_in_month(dt: date):
    # by setting the day to 28 we are guaranteed to be in the last day of the shortest month
    # adding 4 days guarantees that we go into the next month, even if the current month has 31 days
    # taking the day and subtracting it from 32 gives us the number of days in the month we started
    # examples:
    #    dt = 2026-02-15
    #    set day to 28 = 2026-02-28
    #    add 4 days = 2026-03-04
    #    32 - 4 = 28
    #
    #    dt = 2026-06-23
    #    set day to 28 = 2026-06-28
    #    add 4 days = 2026-07-02
    #    32 - 2 = 30
    #    
    #    dt = 2026-10-05
    #    set day to 28 = 2026-10-28
    #    add 4 days = 2026-11-01
    #    32 - 1 = 31
    #
    # this should also work for february 29th
    return 32 - (dt.replace(day=28) + relativedelta(days=4)).day

def number_of_days_in_previous_month(dt: date):
    # by setting the day to 1 and subtracting 1 day we are guaranteed to be in the last day of the previous month
    # we can get the number of days in the previous month by passing that day to the other function
    return number_of_days_in_month(dt.replace(day=1) - relativedelta(days=1))



# this function had to be rewritten because it didn't do a good job at providing month-based intervals
def get_interval_timedelta(interval: str, dt: date | None = None):
    if interval == "daily":
        return relativedelta(days=1)
    elif interval == "weekly":
        return relativedelta(weeks=1)
    elif interval == "fortnightly":
        return relativedelta(weeks=2)
    elif interval == "monthly":
        # when no date is supplied, we cannot determine the exact interval
        if dt is None:
            return relativedelta(months=1)
        
        # if the date is the last day of the month, we can use the number of days in this month to get to the last day of the previous month
        if dt.day == number_of_days_in_month(dt):
            return relativedelta(days=number_of_days_in_month(dt))
        
        # for any other day of the month, we need to use the number of days in the previous month to get to the same day of the previous month
        return relativedelta(days=number_of_days_in_previous_month(dt))
    elif interval == "quarterly":
        # when no date is supplied, we cannot determine the exact interval
        if dt is None:
            return relativedelta(months=3)
        
        # do 3 rounds of monthly intervals
        current_at: date = dt
        for i in range(3):
            current_at: date = current_at - get_interval_timedelta("monthly", current_at)
            
        return relativedelta(days=(dt-current_at).days)
    elif interval == "semiyearly":
        # when no date is supplied, we cannot determine the exact interval
        if dt is None:
            return relativedelta(months=6)

        # do 6 rounds of monthly intervals
        current_at: date = dt
        for i in range(6):
            current_at: date = current_at - get_interval_timedelta("monthly", current_at)

        return relativedelta(days=(dt-current_at).days)
    elif interval == "yearly":
        # when no date is supplied, we cannot determine the exact interval
        if dt is None:
            return relativedelta(years=1)

        # do 12 rounds of monthly intervals
        current_at: date = dt
        for i in range(12):
            current_at: date = current_at - get_interval_timedelta("monthly", current_at)

        return relativedelta(days=(dt-current_at).days)
    else:
        return relativedelta(months=1)