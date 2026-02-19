<script>
import Card from '@/components/Card/index.vue';
import DepositBookTable from '@/components/Tables/DepositBookTable.vue';
import requests from '@/requests';
import DepositAccountsTable from '@/components/Tables/DepositAccountsTable.vue';

export default {
  name: 'depositBook',
  components: {
    DepositAccountsTable,
    DepositBookTable,
    Card,
  },
  data() {
    return {
      book: [],
      loadingBook: true,
      allDates: [],
      transactionBook: [],
      transactionActions: [
        {
          name: 'View',
          icon: 'heroicons-outline:eye',
        },
      ],
    };
  },
  created() {
    requests.getDepositBalances().then((response) => {
      const allDates = Object.keys(response.data['dayBalances'])
        .sort((dateStringA, dateStringB) => (new Date(dateStringA)).getTime() - new Date(dateStringB).getTime())
        .reverse();
      const book = allDates.map((viewDate) => {
        const pageOnDate = response.data['dayBalances'][viewDate];
        const depositAccounts = Object.keys(pageOnDate['balances']);
        const transactionsOnDate = pageOnDate['transactions'].map((transaction) => {
          const diffByAccountString = transaction['diff_by_account'];
          Object.keys(diffByAccountString).forEach((accountName) => {
            diffByAccountString[accountName] = 
              `${diffByAccountString[accountName] > 0 ? '+' : ''}${diffByAccountString[accountName] < 0 ? '-' : ''} £${(Math.abs(diffByAccountString[accountName] / 100)).toFixed(2)}`;
          });
          return {
            details: {
              title: transaction['details']['title'],
              contractId: transaction['details']['contractId'],
            },
            event: transaction['event'],
            ...diffByAccountString,
          };
        });

        const dayDiffByAccountNameString = pageOnDate['diff'];
        depositAccounts.forEach((accountName) => {
          if (dayDiffByAccountNameString.hasOwnProperty(accountName)) {
            dayDiffByAccountNameString[accountName] = 
              `${dayDiffByAccountNameString[accountName] > 0 ? '+' : ''}${dayDiffByAccountNameString[accountName] < 0 ? '-' : ''} £${(Math.abs(dayDiffByAccountNameString[accountName] / 100)).toFixed(2)}`;
          } else {
            dayDiffByAccountNameString[accountName] = '0';
          }
        });

        const dayBalancesByAccountNameString = pageOnDate['balances'];
        depositAccounts.forEach((accountName) => {
          if (dayBalancesByAccountNameString.hasOwnProperty(accountName)) {
            dayBalancesByAccountNameString[accountName] =
              `${dayBalancesByAccountNameString[accountName] > 0 ? '+' : ''}${dayBalancesByAccountNameString[accountName] < 0 ? '-' : ''} £${(Math.abs(dayBalancesByAccountNameString[accountName] / 100)).toFixed(2)}`;
          } else {
            dayBalancesByAccountNameString[accountName] = '0';
          }
        });

        return {
          date: new Date(viewDate),
          columns: [
            {
              label: 'Details',
              field: 'details',
            },
            {
              label: 'Event',
              field: 'event',
            },
            ...depositAccounts.map((accountName) => (
              {
                label: accountName,
                field: accountName,
              }
            )),
          ],
          data: [
            {
              details: {
                title: 'Day Changes',
                contractId: null,
              },
              type: null,
              ...dayDiffByAccountNameString,
              children: transactionsOnDate,

            },
            {
              details: {
                title: 'Balances',
                contractId: null,
              },
              type: null,
              ...dayBalancesByAccountNameString,
              children: [{}],
            },
          ],
        };
      });
      this.loadingBook = false;
      this.book = book;
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card>
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <DepositAccountsTable :loading="loadingBook" :actions="transactionActions"
                              :book="book"></DepositAccountsTable>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
