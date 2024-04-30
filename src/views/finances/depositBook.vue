<script>
import Card from '@/components/Card/index.vue';
import DepositBookTable from '@/components/Tables/DepositBookTable.vue';
import requests from '@/requests';

export default {
  name: 'depositBook',
  components: {
    DepositBookTable,
    Card,
  },
  methods: {
    viewContract(contractId) {
      this.$router.push(`/contracts/${contractId}`);
    },
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
    requests.getDepositBook().then((response) => {
      const allDates = Object.keys(response.data['dayBalances']).sort((dateStringA, dateStringB) => (new Date(dateStringA)).getTime() - new Date(dateStringB).getTime()).reverse();
      const book = allDates.map((viewDate) => {
        const pageOnDate = response.data['dayBalances'][viewDate];
        const depositBearers = Object.keys(pageOnDate['balances']);
        const transactionsOnDate = pageOnDate['transactions'].map((transaction) => {
          const diffByUsernameString = transaction['diff_by_username'];
          Object.keys(diffByUsernameString).forEach((username) => {
            diffByUsernameString[username] = `${diffByUsernameString[username] > 0 ? '+' : ''}${diffByUsernameString[username]}`;
          });
          return {
            title: transaction['title'],
            type: transaction['type'],
            ...diffByUsernameString,
          };
        });

        const dayDiffByUsernameString = pageOnDate['diff'];
        depositBearers.forEach((username) => {
          if (dayDiffByUsernameString.hasOwnProperty(username)) {
            dayDiffByUsernameString[username] = `${dayDiffByUsernameString[username] > 0 ? '+' : ''}${dayDiffByUsernameString[username]}`;
          } else {
            dayDiffByUsernameString[username] = '0';
          }
        });

        return {
          date: new Date(viewDate),
          columns: [
            {
              label: 'Title',
              field: 'title',
            },
            {
              label: 'Type',
              field: 'type',
            },
            ...depositBearers.map((username) => (
                {
                  label: username,
                  field: username,
                }
            )),
          ],
          data: [
            {
              title: 'Total',
              type: null,
              ...dayDiffByUsernameString,
              children: transactionsOnDate,

            },
            {
              title: 'Balances',
              type: null,
              ...pageOnDate['balances'],
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
            <DepositBookTable :loading="loadingBook" :actions="transactionActions" :book="book" :view-contract="viewContract"></DepositBookTable>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>