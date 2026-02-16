<script>
import requests from '@/requests';
import Card from '@/components/Card/index.vue';
import TransactionsTable from '@/components/Tables/TransactionsTable.vue';

export default {
  name: 'transactions',
  components: {TransactionsTable, Card},
  data() {
    return {
      transactions: [],
    };
  },
  mounted() {
    this.fetchTransactions();
  },
  methods: {
    fetchTransactions() {
      requests.getFormattedTransactionHeaders().then((response) => {
        this.transactions = response.data.map((transaction) => ({
          event: transaction.event,
          createdOn: transaction.createdOn,
          createdByUsername: transaction.createdByUsername,
          postedOn: transaction.postedOn,
          postedByUsername: transaction.postedByUsername,
          credit: null,
          debit: null,
          accountName: transaction.accountName,
          children: transaction.formattedTransactionLines.map((line) => ({
            createdOn: null,
            postedOn: null,
            accountName: line.accountName,
            credit: line.credit,
            debit: line.debit,
          })),
        }));
      });
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card title="Accounts Management" class="dark:text-slate-300 text-slate-700">
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <TransactionsTable :transactions="transactions"/>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>