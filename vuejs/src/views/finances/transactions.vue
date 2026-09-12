<script>
import requests from '@/requests';
import Card from '@/components/Card/index.vue';
import TransactionsTable from '@/components/Tables/TransactionsTable.vue';
import Pagination from '@/components/Pagination/index.vue';

export default {
  name: 'transactions',
  components: {Pagination, TransactionsTable, Card},
  data() {
    return {
      transactions: [],
      loading: true,
      currentPage: 1,
      perPage: 10,
    };
  },
  mounted() {
    this.fetchTransactions();
  },
  methods: {
    transactionSorting(a, b) {
      return new Date(b.createdOn) - new Date(a.createdOn);
    },
    fetchTransactions() {
      requests.getFormattedTransactionHeaders().then((response) => {
        this.transactions = response.data
          .map((transaction) => ({
            id: transaction.id,
            event: transaction.event,
            createdOn: transaction.createdOn,
            createdByUsername: transaction.createdByUsername,
            postedOn: transaction.postedOn,
            postedByUsername: transaction.postedByUsername,
            credit: null,
            debit: null,
            accountName: transaction.accountName,
            children: transaction.formattedTransactionLines.map((line) => ({
              id: line.id,
              createdOn: null,
              postedOn: null,
              accountName: line.accountName,
              credit: line.credit,
              debit: line.debit,
            })),
          }))
          .sort(this.transactionSorting);
        this.loading = false;
      });
    },
  },
  computed: {
    transactionsPaged() {
      return this.transactions.slice((this.currentPage - 1) * this.perPage, this.currentPage * this.perPage);
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card title="Transaction History" class="dark:text-slate-300 text-slate-700">
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <Pagination
              :total="transactions.length"
              :current="currentPage"
              @page-changed="(page) => currentPage = page"
              :per-page="perPage"
              :pageRange="5"
            />
            <TransactionsTable :loading="loading" :transactions="transactionsPaged"/>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
