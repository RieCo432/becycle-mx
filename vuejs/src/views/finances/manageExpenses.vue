<script>
import ExpenseSummaryTable from '@/components/Tables/ExpenseSummaryTable.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import DashButton from '@/components/Button/index.vue';
import Modal from '@/components/Modal/Modal.vue';
import EditExpenseModal from '@/components/Modal/EditExpenseModal.vue';

const toast = useToast();

export default {
  name: 'manageExpenses',
  components: {
    EditExpenseModal,
    DashButton,
    ExpenseSummaryTable,
    Card,
    Modal,
  },
  data() {
    return {
      loadingExpenses: true,
      isUserTreasurer: false,
      isUserAdmin: false,
      expenses: [],
      expenseInfo: {},
      showExpenseInfoModal: false,
      showExpenseEditModal: false,
      editExpense: null,
      receiptUrl: null,
      filterByTag: null,
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
          label: 'Tag',
          field: 'tag.id',
          filterOptions: {
            enabled: true,
            placeholder: 'No Filter',
            filterDropdownItems: [],
          },
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
        this.expenses.splice(indexInArray, 1, this.setExpenseStatus(response.data));
        this.closeExpenseInfoModal();
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    deleteExpense(expenseId) {
      const confirmed = confirm('Are you sure you want to delete this expense?');
      if (confirmed) {
        requests.deleteExpense(expenseId).then((response) => {
          toast.warning('Expense Deleted', {timeout: 2000});
          const indexInArray = this.expenses.findIndex((e) => (e.id === expenseId));
          this.expenses.splice(indexInArray, 1);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
      }
    },
    getExpenses() {
      requests.getExpenses(this.filterByTag).then((response) => {
        this.expenses = response.data.map((expense) => this.setExpenseStatus(expense));
        this.loadingExpenses = false;
      });
    },
    closeExpenseInfoModal() {
      this.showExpenseInfoModal = false;
      this.receiptUrl = null;
    },
    openEditExpenseModal(expenseId) {
      this.editExpense = this.expenses.find((e) => e.id === expenseId);
      this.showExpenseEditModal = true;
    },
    closeExpenseEditModal() {
      this.showExpenseEditModal = false;
      this.editExpense = null;
    },
    expenseUpdated(updatedExpense) {
      const indexInArray = this.expenses.findIndex((e) => (e.id === updatedExpense.id));
      this.expenses.splice(indexInArray, 1, updatedExpense);
    },
    setExpenseStatus(expense) {
      return {...expense, status: expense.transferDate ? 'Closed' : 'Open'};
    },
  },
  created() {
    this.getExpenses();
    requests.getExpenseTags(true).then((response) => {
      const tagColumnIndex = this.columns.findIndex((column) => (column.field === 'tag.id'));
      this.columns[tagColumnIndex]
        .filterOptions.filterDropdownItems.splice(0, this.columns[tagColumnIndex].length, ...response.data.map((tag) => (`${tag.id}`)));
    });
    requests.getUserMe().then((response) => {
      this.isUserTreasurer = response.data.treasurer;
      this.isUserAdmin = response.data.admin;
      if (this.isUserTreasurer) {
        this.actions.push({
          id: 'markTransferred',
          label: 'Mark as transferred',
          icon: 'heroicons-outline:arrows-right-left',
          func: (expenseId) => this.patchExpenseTransferred(expenseId),
        });
      }
      if (this.isUserAdmin) {
        this.actions.push({
          id: 'editExpense',
          label: 'Edit Expense',
          icon: 'heroicons-outline:pencil',
          func: (expenseId) => this.openEditExpenseModal(expenseId),
        });
        this.actions.push({
          id: 'delete',
          label: 'Delete expense',
          icon: 'heroicons-outline:trash',
          func: (expenseId) => this.deleteExpense(expenseId),
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
        <ExpenseSummaryTable  title="Expenses" :loading="loadingExpenses"
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
    <EditExpenseModal
        :show-modal="showExpenseEditModal"
        :expense="editExpense"
        :close-modal="closeExpenseEditModal"
        @expense-updated="expenseUpdated"
        @close="closeExpenseEditModal"
    ></EditExpenseModal>
  </div>
</template>

<style scoped lang="scss">

</style>
