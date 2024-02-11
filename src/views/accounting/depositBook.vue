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
      viewDate: new Date().toDateString(),
      allDates: [],
      loadingBook: true,
      transactionBook: [],
      depositBearers: [],
      depositBearersColumns: [],
      transactionActions: [
        {
          name: 'View',
          icon: 'heroicons-outline:eye',
        },
      ],
      transactionsColumns: [],
    };
  },
  computed: {
    tableTitle() {
      const d = new Date(this.viewDate);
      return 'Deposits on ' + d.toDateString();
    },
  },
  created() {
    requests.getDepositBook().then((response) => {
      this.allDates = Object.keys(response.data['dayBalances']).sort((dateString) => (new Date(dateString))).reverse();
      this.viewDate = this.allDates[0];
      const pageOnDate = response.data['dayBalances'][this.viewDate];
      console.log(pageOnDate);
      this.depositBearers = Object.keys(pageOnDate['balances']);
      this.depositBearersColumns = this.depositBearers.map((username) => (
          {
            label: username,
            field: username,
          }
      ));
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
      this.depositBearers.forEach((username) => {
        dayDiffByUsernameString[username] = `${dayDiffByUsernameString[username] > 0 ? '+' : ''}${dayDiffByUsernameString[username]}`;
      });

      this.transactionsColumns = [
        {
          label: 'Title',
          field: 'title',
        },
        {
          label: 'Type',
          field: 'type',
        },
          ...this.depositBearersColumns,
        {
          label: 'Action',
          field: 'action',
        },
      ];
      this.transactionBook = [
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
      ];
      this.loadingBook = false;
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
            <DepositBookTable :loading="loadingBook" :deposit-bearers="depositBearers" :actions="transactionActions" :columns="transactionsColumns" :advanced-table="transactionBook" :title="tableTitle" :view-contract="viewContract"></DepositBookTable>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>