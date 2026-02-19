<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import AccountsTable from '@/components/Tables/AccountsTable.vue';
import AddNewAccountCard from '@/components/Card/AddNewAccountCard.vue';
import {useToast} from 'vue-toastification';
import EditAccountModal from '@/components/Modal/EditAccountModal.vue';

const toast = useToast();

export default {
  name: 'accounts',
  components: {EditAccountModal, AddNewAccountCard, AccountsTable, Card},
  data() {
    return {
      accounts: null,
      showEditAccountModal: false,
      selectedAccount: null,
    };
  },
  mounted() {
    this.fetchAccounts();
  },
  methods: {
    fetchAccounts() {
      requests.getAccounts().then((response) => {
        this.accounts = response.data;
      });
    },
    closeAccount(accountId) {
      requests.closeAccount(accountId)
        .then(() => {
          toast.success('Account Closed!', {timeout: 2000});
          this.fetchAccounts();
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    },
    reopenAccount(accountId) {
      requests.reopenAccount(accountId)
        .then(() => {
          toast.success('Account Reopened!', {timeout: 2000});
          this.fetchAccounts();
        })
        .catch(() => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    },
    editAccount(accountId) {
      this.selectedAccount = this.accounts.find((account) => account.id === accountId);
      this.showEditAccountModal = true;
    },
  },
};

</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="2xl:col-span-9 col-span-12">
      <Card title="Accounts Management" class="dark:text-slate-300 text-slate-700">
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <AccountsTable
                    :accounts="accounts"
                    @reopen-account="reopenAccount"
                    @close-account="closeAccount"
                    :edit-account="editAccount"
            />
          </div>
        </div>
      </Card>
    </div>
    <div v-if="accounts !== null" class="2xl:col-span-3 col-span-12">
      <AddNewAccountCard
              :accounts="accounts"
              @accountCreated="fetchAccounts"/>
    </div>
    
    <EditAccountModal
      v-if="accounts !== null && selectedAccount !== null"
      :show-modal="showEditAccountModal"
              :account="selectedAccount"
              @accountUpdated="fetchAccounts"
      :close-modal="() => {showEditAccountModal = false; selectedAccount = null;}"
      :accounts="accounts"/>
  </div>
</template>

<style scoped lang="scss">

</style>
