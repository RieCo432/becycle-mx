<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import AccountsTable from '@/components/Tables/AccountsTable.vue';
import AddNewAccountCard from '@/components/Card/AddNewAccountCard.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'accounts',
  components: {AddNewAccountCard, AccountsTable, Card},
  data() {
    return {
      accounts: null,
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
  </div>
</template>

<style scoped lang="scss">

</style>
