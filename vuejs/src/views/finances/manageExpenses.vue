<script>
import ExpenseSummaryTable from '@/components/Tables/ExpenseSummaryTable.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import DashButton from '@/components/Button/index.vue';
import Modal from '@/components/Modal/Modal.vue';

const toast = useToast();

export default {
  name: 'manageExpenses',
  components: {
    DashButton,
    ExpenseSummaryTable,
    Card,
    Modal,
  },
  data() {
    return {
      loadingExpenses: true,
      isUserTreasurer: false,
      expenses: [],
      expenseInfo: {},
      showExpenseInfoModal: false,
      receiptUrl: null,
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
      actions: [
        {
          id: 'viewReceipt',
          label: 'View Receipt',
          icon: 'heroicons-outline:receipt-percent',
          func: (expenseId) => {
            this.expenseInfo = this.expenses.find((e) => e.id === expenseId);
            requests.getExpenseReceipt(expenseId).then((response) => {
              this.receiptUrl = window.URL.createObjectURL(new Blob([response.data], {type: this.expenseInfo.receiptContentType}));
            });
            this.showExpenseInfoModal = true;
          },
        },
      ],
    };
  },
  methods: {
    patchExpenseTransferred(expenseId) {
      requests.patchExpenseTransferred(expenseId).then((response) => {
        toast.success('Expense Transferred', {timeout: 2000});
        const indexInArray = this.expenses.findIndex((e) => (e.id === response.data.id));
        this.expenses.splice(indexInArray, 1, response.data);
        this.closeExpenseInfoModal();
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
    closeExpenseInfoModal() {
      this.showExpenseInfoModal = false;
      this.receiptUrl = null;
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
        <ExpenseSummaryTable title="Expenses" :loading="loadingExpenses"
                             :columns="columns" :data="expenses" :actions="actions"></ExpenseSummaryTable>
      </Card>
    </div>
    <Modal @close="closeExpenseInfoModal()" :active-modal="showExpenseInfoModal" size-class="max-w-5xl" title="Expense Details">
      <div v-if="showExpenseInfoModal" class="grid grid-cols-6 lg:grid-cols-12">
        <div class="col-span-4 text-base text-slate-700 dark:text-slate-300">
          <p>Volunteer: {{ expenseInfo.expenseUser.username }}</p>
          <p>Expense Date: {{ new Date(Date.parse(expenseInfo.expenseDate))
              .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'}) }}</p>
          <p>Amount: &#163; {{ expenseInfo.amount.toFixed(2) }}</p>
          <p>Type: {{ expenseInfo.type }}</p>
          <p>Notes: {{ expenseInfo.notes }}</p>
          <p v-if="expenseInfo.transferDate !== null">Transfer Date: {{ new Date(Date.parse(expenseInfo.transferDate))
              .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'}) }}</p>
          <p v-if="expenseInfo.treasurerUser !== null">Treasurer: {{ expenseInfo.treasurerUser.username }}</p>
        </div>
        <div v-if="receiptUrl !== null" class="col-span-8">
          <img v-if="expenseInfo.receiptContentType.startsWith('image')" :src="receiptUrl" alt="Receipt"/>
          <iframe v-if="expenseInfo.receiptContentType === 'application/pdf'"
                  class="w-full h-[700px]" :src="receiptUrl" type="application/pdf"></iframe>
        </div>
      </div>
      <div v-if="expenseInfo.transferDate === null && isUserTreasurer"
           class="px-4 justify-end py-3 flex space-x-3 border-t border-slate-100 dark:border-slate-700">
        <DashButton
            @click="patchExpenseTransferred(expenseInfo.id)"
        >Mark As Transferred</DashButton>
      </div>
    </Modal>
  </div>
</template>

<style scoped lang="scss">

</style>
