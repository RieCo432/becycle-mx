<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Modal from '@/components/Modal/Modal.vue';
import ExpenseClaimSummaryTable from '@/components/Tables/ExpenseClaimSummaryTable.vue';
import TransactionLinesTable from '@/components/Tables/TransactionLinesTable.vue';
import TransactionReimbursementForm from '@/components/Forms/TransactionReimbursementForm.vue';
import EditExpenseClaimModal from '@/components/Modal/EditExpenseClaimModal.vue';

const toast = useToast();

export default {
  name: 'manageExpenseClaims',
  components: {
    EditExpenseClaimModal,
    TransactionReimbursementForm,
    TransactionLinesTable,
    ExpenseClaimSummaryTable,
    Card,
    Modal,
  },
  data() {
    return {

      loadingExpenseClaims: true,
      isUserTreasurer: false,
      isUserAdmin: false,
      expenseClaims: [],
      expenseClaimInfo: {},
      showExpenseClaimInfoModal: false,
      showExpenseClaimEditModal: false,
      editExpenseClaim: null,
      receiptUrl: null,
      columns: [
        {
          label: 'Status',
          field: 'status',
        },
        {
          label: 'Expense Date',
          field: 'expenseDate',
        },
        {
          label: 'Amount',
          field: 'amount',
        },
        {
          label: 'Project',
          field: 'projectId',
        },
        {
          label: 'Added By',
          field: 'expenseTransactionHeader.postedByUser.username',
        },
        {
          label: 'Notes',
          field: 'notes',
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
          func: (expenseClaimId) => {
            this.expenseClaimInfo = this.expenseClaimsProcessed.find((e) => e.id === expenseClaimId);
            requests.getExpenseClaimReceipt(expenseClaimId).then((response) => {
              this.receiptUrl = window.URL.createObjectURL(new Blob([response.data], {type: this.expenseClaimInfo.receiptContentType}));
            });
            this.showExpenseClaimInfoModal = true;
          },
        },
        {
          id: 'editExpense',
          label: 'Edit Expense',
          icon: 'heroicons-outline:pencil',
          func: (expenseId) => this.openEditExpenseClaimModal(expenseId),
        },
        {
          id: 'delete',
          label: 'Delete expense',
          icon: 'heroicons-outline:trash',
          func: (expenseId) => this.deleteExpenseClaim(expenseId),
        },
      ],
    };
  },
  methods: {
    deleteExpenseClaim(expenseClaimId) {
      if (confirm('Are you sure you want to delete this expense?')) {
        requests.deleteExpenseClaim(expenseClaimId).then(() => {
          toast.warning('Expense Deleted', {timeout: 2000});
          const indexInArray = this.expenseClaims.findIndex((e) => (e.id === expenseClaimId));
          this.expenseClaims.splice(indexInArray, 1);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
      }
    },
    getExpenseClaims() {
      requests.getExpenseClaims(this.filterByTag).then((response) => {
        this.expenseClaims = response.data;
        this.loadingExpenseClaims = false;
      });
    },
    closeExpenseInfoModal() {
      this.showExpenseClaimInfoModal = false;
      this.receiptUrl = null;
    },
    openEditExpenseClaimModal(expenseId) {
      this.editExpenseClaim = this.expenseClaims.find((e) => e.id === expenseId);
      this.showExpenseClaimEditModal = true;
    },
    closeExpenseEditModal() {
      this.showExpenseClaimEditModal = false;
      this.editExpenseClaim = null;
    },
    expenseClaimUpdated(updatedExpenseClaim) {
      const indexInArray = this.expenseClaims.findIndex((e) => (e.id === updatedExpenseClaim.id));
      this.expenseClaims.splice(indexInArray, 1, updatedExpenseClaim);
      this.closeExpenseEditModal();
    },
    expenseClaimReimbursed(expenseClaim) {
      if (this.showExpenseClaimInfoModal) this.expenseClaimInfo = expenseClaim;
      const indexInArray = this.expenseClaims.findIndex((e) => (e.id === expenseClaim.id));
      this.expenseClaims.splice(indexInArray, 1, expenseClaim);
      this.closeExpenseInfoModal();
    },
    getExpenseStatus(expenseClaim) {
      const expenseLiabilityTxLine = expenseClaim.expenseTransactionHeader
        .transactionLines
        .find((line) => line.account.type === 'liability');
      const reimbursementLiabilityTxLine = expenseClaim.reimbursementTransactionHeader ?
        expenseClaim.reimbursementTransactionHeader
          .transactionLines
          .find((line) => line.account.type === 'liability') :
        null;

      if (!expenseLiabilityTxLine) return 'Paid In Advance';
      if (!reimbursementLiabilityTxLine) return 'Pending';
      if (Math.abs(expenseLiabilityTxLine.amount) > Math.abs(reimbursementLiabilityTxLine.amount)) return 'Partially Paid';
      return 'Paid';
    },
  },
  computed: {
    expenseClaimsProcessed() {
      return this.expenseClaims.map((expenseClaim) => ({
        ...expenseClaim,
        status: this.getExpenseStatus(expenseClaim),
        projectId: expenseClaim
          .expenseTransactionHeader
          .transactionLines
          .find((line) => line.account.type === 'expense')
          .account
          .restrictedToProjectId,
      }));
    },
  },
  created() {
    this.getExpenseClaims();
    requests.getUserMe().then((response) => {
      this.isUserTreasurer = response.data.treasurer;
      this.isUserAdmin = response.data.admin;
    });
  },
};
</script>

<template>
  <div>
    <div class="grid grid-cols-12">
      <div class="col-span-full">
        <Card>
          <ExpenseClaimSummaryTable title="Expense Claims" :loading="loadingExpenseClaims"
                                    :columns="columns" :data="expenseClaimsProcessed" :actions="actions"></ExpenseClaimSummaryTable>
        </Card>
      </div>
  </div>

    <Modal
      @close="closeExpenseInfoModal()"
      :active-modal="showExpenseClaimInfoModal"
      size-class="max-w-[1700px] h-[1000px]" title="Expense Details">
      <div v-if="showExpenseClaimInfoModal && expenseClaimInfo" class="grid grid-cols-6 lg:grid-cols-12 h-full">
        <div class="col-span-4 text-base text-slate-700 dark:text-slate-300 h-full">
          <p>Volunteer: {{ expenseClaimInfo.expenseTransactionHeader.postedByUser.username }}</p>
          <p>Expense Date: {{
              new Date(Date.parse(expenseClaimInfo.expenseDate))
                .toLocaleDateString(undefined, {weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})
            }}</p>
          <p>Notes: {{ expenseClaimInfo.notes }}</p>
          <div>
            <p>Expense Transaction:</p>
            <TransactionLinesTable :transaction-header="expenseClaimInfo.expenseTransactionHeader"/>
          </div>
          <div>
            <p class="font-bold">Reimbursement Transaction:</p>
            <TransactionLinesTable
              v-if="expenseClaimInfo.reimbursementTransactionHeaderId !== null"
              :transaction-header="expenseClaimInfo.reimbursementTransactionHeader"/>
            <TransactionReimbursementForm
              v-else-if="expenseClaimInfo.status === 'Pending'"
              :expense-claim-info="expenseClaimInfo"
              @expense-reimbursed="expenseClaimReimbursed"/>
          </div>

        </div>
        <div v-if="receiptUrl !== null" class="col-span-8 min-h-full">
          <img v-if="expenseClaimInfo.receiptContentType.startsWith('image')" :src="receiptUrl" alt="Receipt" class="w-full h-auto"/>
          <iframe v-if="expenseClaimInfo.receiptContentType === 'application/pdf'"
                  class="w-full h-full" :src="receiptUrl" type="application/pdf"></iframe>
        </div>
      </div>
    </Modal>
    <EditExpenseClaimModal
        :show-modal="showExpenseClaimEditModal"
        :expense-claim="editExpenseClaim"
        :close-modal="closeExpenseEditModal"
        @expense-claim-updated="expenseClaimUpdated"
        @close="closeExpenseEditModal"
    ></EditExpenseClaimModal>
  </div>
</template>

<style scoped lang="scss">

</style>
