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
    const now = new Date();
    if (!d) {
      return '';
    }
    const parsedDate = new Date(Date.parse(`${d}Z`));
    
    const isToday =
      parsedDate.getDate() === now.getDate() &&
      parsedDate.getMonth() === now.getMonth() &&
      parsedDate.getFullYear() === now.getFullYear();
    const isYesterday =
      parsedDate.getDate() === now.getDate() - 1 &&
      parsedDate.getMonth() === now.getMonth() &&
      parsedDate.getFullYear() === now.getFullYear();
    if (isToday || isYesterday) {
      return `${isYesterday ? 'Yesterday ' : ''}${parsedDate.toLocaleString(undefined, {hour: 'numeric', minute: 'numeric'})}`;
    }

    return parsedDate.toLocaleDateString(undefined, {year: 'numeric', month: 'short', day: 'numeric'});
  },
};
