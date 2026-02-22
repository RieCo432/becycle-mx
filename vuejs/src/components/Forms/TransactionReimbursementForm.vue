<script>
import Button from '@/components/Button/index.vue';
import Select from '@/components/Select/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import TextInput from '@/components/TextInput/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {ref, toRef} from 'vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'TransactionReimbursementForm',
  components: {TextInput, ComboboxTextInput, Select, Button},
  setup(props, context) {
    const projects = ref([]);
    const assetAccounts = ref([]);

    const expenseClaimInfo = toRef(props, 'expenseClaimInfo');

    const transactionLineOnLiabilityAccount = expenseClaimInfo.value
      .expenseTransactionHeader
      .transactionLines
      .find((line) => line.account.type === 'liability');
    
    const amountOnLiabilityAccount = transactionLineOnLiabilityAccount ? Math.abs(transactionLineOnLiabilityAccount.amount) : 0;
    const liabilityAccountId = transactionLineOnLiabilityAccount ? transactionLineOnLiabilityAccount.accountId : null;
    
    const projectIdOfExpenseAccount = expenseClaimInfo.value
      .expenseTransactionHeader
      .transactionLines
      .find((line) => line.account.type === 'expense')
      .account.restrictedToProjectId;
    
    console.log('project id of expense account', projectIdOfExpenseAccount);

    console.log('amount claimed', amountOnLiabilityAccount);

    const expenseReimbursementSchema = yup.object().shape({
      projectId: yup.string().required(),
      amount: yup.number().required().max(amountOnLiabilityAccount / 100).min(0),
      assetAccount: yup.object().shape({
        id: yup.string().uuid().required(' The asset account id is required '),
        name: yup.string().required(' The asset account name is required '),
      }).required(' The asset account is required '),
    });


    const {handleSubmit, handleReset: resetExpenseReimbursementForm} = useForm({
      validationSchema: expenseReimbursementSchema,
      keepValuesOnUnmount: true,
      initialValues: {
        assetAccount: {name: null, id: null},
      },
    });

    const {value: projectId, errorMessage: projectIdError, setErrors: setProjectIdErrors} = useField('projectId');
    const {value: amount, errorMessage: amountError} = useField('amount');
    const {value: assetAccount, errorMessage: assetAccountError, resetField: resetAssetAccount} = useField('assetAccount');

    const submitExpenseReimbursement = handleSubmit(() => {
      console.log(projectId.value);
      if ((projectId.value === 'null' ? null : projectId.value) !== projectIdOfExpenseAccount) {
        setProjectIdErrors('The projectId of the asset account must match the projectId of the expense account');
      }
      
      const reimbursementTransactionDraft = {
        transactionHeader: {
          event: 'expense_reimbursed',
        },
        transactionLines: [
          {amount: -amount.value * 100, accountId: assetAccount.value.id},
          {amount: amount.value * 100, accountId: liabilityAccountId},
        ],
        attemptAutoPost: false,
      };
      
      requests.createTransaction(reimbursementTransactionDraft).then((response) => {
        toast.success('Reimbursement Transaction Created!', {timeout: 2000});
        
        const transactionHeaderId = response.data.id;
        
        requests.patchExpenseClaimReimbursed(expenseClaimInfo.value.id, transactionHeaderId).then((response) => {
          toast.success('Expense Reimbursed!', {timeout: 2000});
          context.emit('expenseReimbursed', response.data);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      projects,
      assetAccounts,
      projectId,
      projectIdError,
      amount,
      amountError,
      assetAccount,
      assetAccountError,
      submitExpenseReimbursement,
      resetAssetAccount,
    };
  },
  methods: {
    fetchProjects() {
      requests.getProjects().then((response) => {
        this.projects = [
          {label: 'No Project', value: 'null'},
          ...response.data.map((t) => (
            {
              label: `${t.id} --- ${t.description}`,
              value: t.id,
            }
          ))];
      });
    },
    fetchAssetAccounts() {
      requests.getAccounts([
        {name: 'types', value: 'asset'},
        {name: 'for_user', value: true},
        {name: 'ui_filters', value: 'transfer'},
        ...(this.projectId && this.projectId !== 'null' ? [{name: 'project_id', value: this.projectId}] : [])]).then((response) => {
        this.assetAccounts = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 5000});
      });
      this.resetAssetAccount();
    },
    selectAssetAccount(event, i) {
      if (i !== -1) {
        this.assetAccount = this.filtered_asset_account_suggestions[i];
        console.log(this.filtered_asset_account_suggestions[i]);
        console.log(this.assetAccount);
        this.userSelectionOptionsStatic = false;
      }
    },
    makeAccountLegible(account) {
      return `${account.name}`;
    },
  },
  created() {
    this.fetchAssetAccounts();
    this.fetchProjects();
  },
  computed: {
    filtered_asset_account_suggestions() {
      return this.assetAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.assetAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
  },
  props: {
    expenseClaimInfo: {
      type: Object,
      required: true,
    },
  },
  emits: ['expenseReimbursed'],
};
</script>

<template>
  <div>
    <form @submit.prevent="submitExpenseReimbursement">
      <div class="grid grid-cols-6 xl:grid-cols-6 gap-5">

        <div class="col-span-6">
          <Select
            :options="projects"
            label="Tag/Project"
            v-model="projectId"
            name="projectId"
            placeholder="Is this for a specific project? If so, select it here."
            :error="projectIdError"
            @change="fetchAssetAccounts"
          />
        </div>

        <div class="col-span-6" >
          <TextInput
            label="Amount (&pound;)"
            type="text"
            placeholder="12.34"
            name="amount"
            v-model="amount"
            :error="amountError"
          />
        </div>

        <div class="col-span-6" >
          <ComboboxTextInput
            :field-model-value="assetAccount.name"
            :suggestions="filtered_asset_account_suggestions.map(makeAccountLegible)"
            :selected-callback="selectAssetAccount"
            :allow-new="false"
            :open-by-default="false"
            label="Asset Account"
            type="text"
            placeholder="workshop"
            name="assetAccount"
            v-model="assetAccount.name"
            :error="assetAccountError"
            @change="() => {}"
          />
        </div>
        <div class="col-span-full">
          <Button type="submit" class="btn block w-full text-center">
            Submit
          </Button>
        </div>
      </div>
    </form>
  </div>
</template>

<style scoped lang="scss">

</style>
