import {
  differenceInCalendarDays,
  differenceInCalendarMonths,
  differenceInSeconds,
  format,
  formatDistanceToNow,
  isThisYear,
  isToday,
  isValid,
  isYesterday,
  parseISO,
} from 'date-fns';

export default {
  getFinancialYear() {
    const financialYearStartMonth = 3; // April
    const financialYearEndDate = 31; // last day of previous month

    const start = new Date();
    start.setDate(1);
    if (start.getMonth() < financialYearStartMonth) {
      start.setUTCFullYear(start.getUTCFullYear() - 1);
    }
    start.setMonth(financialYearStartMonth);

    const end = new Date();
    if (end.getMonth() > financialYearStartMonth) {
      end.setUTCFullYear(end.getUTCFullYear() + 1);
    }
    end.setMonth(financialYearStartMonth - 1);
    end.setDate(financialYearEndDate);

    return {
      start,
      end,
    };
  },
  getPastSixMonths() {
    const end = new Date();
    const start = new Date(end);
    if (start.getMonth() < 6) {
      start.setUTCFullYear(start.getUTCFullYear() - 1);
    }
    start.setMonth(start.getMonth() - 6);

    return {
      start,
      end,
    };
  },
  convertDateToPickerString(d) {
    return d.toISOString().split('T')[0];
  },
  convertToConvenientString(d) {
    if (!d) {
      return '';
    }

    const parsedDate = parseISO(`${d}Z`);

    if (!isValid(parsedDate)) {
      return '';
    }

    const now = new Date();
    const secondsAgo = differenceInSeconds(now, parsedDate);
    const calendarDaysAgo = differenceInCalendarDays(now, parsedDate);
    const calendarMonthsAgo = differenceInCalendarMonths(now, parsedDate);

    if (secondsAgo < 30) {
      return 'Just now';
    }

    if (secondsAgo < 86400 && isToday(parsedDate)) {
      return formatDistanceToNow(parsedDate, {addSuffix: true});
    }

    if (isYesterday(parsedDate)) {
      return `Yesterday at ${format(parsedDate, 'HH:mm')}`;
    }

    if (calendarDaysAgo < 7) {
      return format(parsedDate, 'EEEE HH:mm');
    }

    if (calendarDaysAgo < 14) {
      return 'Last week';
    }

    if (calendarDaysAgo < 31) {
      return formatDistanceToNow(parsedDate, {addSuffix: true});
    }

    if (calendarMonthsAgo === 1) {
      return 'Last month';
    }

    if (calendarMonthsAgo < 12) {
      return formatDistanceToNow(parsedDate, {addSuffix: true});
    }

    if (calendarMonthsAgo < 24) {
      return 'Last year';
    }

    return format(parsedDate, isThisYear(parsedDate) ? 'd MMM' : 'd MMM yyyy');
  },
};
