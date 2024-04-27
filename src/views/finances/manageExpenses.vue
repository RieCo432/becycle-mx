<script>
import ExpenseSummaryTable from '@/components/Tables/ExpenseSummaryTable.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'manageExpenses',
  components: {
    ExpenseSummaryTable,
    Card,
  },
  data() {
    return {
      loadingExpenses: true,
      isUserTreasurer: false,
      expenses: [],
      columns: [
        {
          label: 'Status',
          field: 'status',
        },
        {
          label: ' Expense Date',
          field: 'expenseDate',
        },
        {
          label: 'Amount',
          field: 'amount',
        },
        {
          label: 'Volunteer',
          field: 'expenseUser.username',
        },
        {
          label: 'Type',
          field: 'type',
        },
        {
          label: 'Notes',
          field: 'notes',
        },
        {
          label: 'Transfer Date',
          field: 'transferDate',
        },
        {
          label: 'Treasurer',
          field: 'treasurerUser.username',
        },
        {
          label: 'Actions',
          field: 'actions',
        },
      ],
      actions: [],
    };
  },
  methods: {
    patchExpenseTransferred(expenseId) {
      requests.patchExpenseTransferred(expenseId).then((response) => {
        toast.success('Expense Transferred', {timeout: 2000});
        const indexInArray = this.expenses.findIndex((e) => (e.id === response.data.id));
        this.expenses.splice(indexInArray, 1, response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    getExpenses() {
      requests.getExpenses().then((response) => {
        this.expenses = response.data;
        this.loadingExpenses = false;
      });
    },
  },
  mounted() {
    this.getExpenses();
    requests.getUserMe().then((response) => {
      this.isUserTreasurer = response.data.treasurer;
      if (this.isUserTreasurer) {
        this.actions.push({
          id: 'markTransferred',
          label: 'Mark as transferred',
          icon: 'heroicons-outline:arrows-right-left',
          func: (expenseId) => this.patchExpenseTransferred(expenseId),
        });
      }
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12">
    <div class="col-span-full">
      <Card>
        <ExpenseSummaryTable title="Expenses" :loading="loadingExpenses" :columns="columns" :data="expenses" :actions="actions"></ExpenseSummaryTable>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
