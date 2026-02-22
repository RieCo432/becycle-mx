<script>
import requests from '@/requests';
import {useDropzone} from 'vue3-dropzone';
import Card from '@/components/Card/index.vue';
import * as yup from 'yup';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';
import Select from '@/components/Select/index.vue';
import Textarea from '@/components/Textarea/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import Button from '@/components/Button/index.vue';
import {computed, ref} from 'vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import Checkbox from '@/components/Checkbox/index.vue';

const toast = useToast();

export default {
  name: 'newExpenseClaim',
  components: {
    Checkbox,
    ComboboxTextInput,
    Button,
    TextInput,
    Textarea,
    Select,
    Card,
    ErrorMessage,
  },
  setup() {
    function onDrop(acceptFiles) {
      files.value = acceptFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
          contentType: file.type,
        }),
      );
    }

    const liabilityAccounts = ref([]);
    const expenseAccounts = ref([]);
    const assetAccounts = ref([]);

    const {getRootProps, getInputProps, ...rest} = useDropzone({onDrop, multiple: false});
    const userSelectionOptionsStatic = ref(true);
    
    function fetchAssetAccounts() {
      requests.getAccounts([
        {name: 'types', value: 'asset'},
        {name: 'for_user', value: true},
        {name: 'ui_filters', value: 'expense'}]).then((response) => {
        assetAccounts.value = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 5000});
      });
    }

    const newExpenseSchemas = yup.object().shape({
      projectId: yup.string().required(),
      notes: yup.string().required(),
      amount: yup.number().required(),

      expenseAccount: yup.object().shape({
        id: yup.string().uuid().required(' The expense account id is required '),
        name: yup.string().required(' The expense account name is required '),
      }).required(' The expense account is required '),

      useAdvance: yup.boolean().nullable(),

      liabilityAccount: yup.object().shape({
        id: yup.string().uuid().required(' The liability account id is required '),
        name: yup.string().required(' The liability account name is required '),
      }).required(' The liability account is required '),

      assetAccount: yup.object().when('useAdvance', {
        is: true,
        then: () => yup.object().shape({
          id: yup.string().uuid().required(' The asset account id is required '),
          name: yup.string().required(' The asset account name is required ')})
          .required('This is required if you wish to use your advance.'),
        otherwise: () => yup.object().nullable(),
      }),
      expenseDate: yup.date().nullable(),
      file: yup.array().length(1),
    });


    const {handleSubmit, handleReset: resetExpenseForm} = useForm({
      validationSchema: newExpenseSchemas,
      keepValuesOnUnmount: true,
    });

    const {value: projectId, errorMessage: projectIdError} = useField('projectId');
    const {value: notes, errorMessage: notesError} = useField('notes');
    const {value: amount, errorMessage: amountError} = useField('amount');
    const {value: useAdvance, errorMessage: useAdvanceError} = useField('useAdvance');
    const {value: expenseAccount, errorMessage: expenseAccountError} = useField('expenseAccount');
    const {value: liabilityAccount, errorMessage: liabilityAccountError} = useField('liabilityAccount');
    const {value: assetAccount, errorMessage: assetAccountError} = useField('assetAccount');

    const {value: expenseDate, errorMessage: expenseDateError, setErrors: setExpenseDateErrors} = useField('expenseDate');
    const {value: files, errorMessage: fileError} = useField('file', undefined, {initialValue: []});

    liabilityAccount.value = {name: null, id: null};
    assetAccount.value = {name: null, id: null};
    expenseAccount.value = {name: null, id: null};

    

    const submitNewExpense = handleSubmit(() => {
      if (!expenseDate.value || !expenseDate.value.length) {
        setExpenseDateErrors('This field is required');
        return;
      }

      const totalAmount = amount.value * 100;
      const amountFromAdvance = assetAccount.value.id ? Math.min(totalAmount, assetAccount.value.balance) : 0;
      const amountFromLiability = totalAmount - amountFromAdvance;

      const expenseTransactionsHeaderDraft = {
        transactionHeader: {
          event: 'expense_claimed',
        },
        transactionLines: [
          {amount: totalAmount, accountId: expenseAccount.value.id},
          ...(amountFromAdvance > 0 ? [{amount: -amountFromAdvance, accountId: assetAccount.value.id}] : []),
          ...(amountFromLiability > 0 ? [{amount: -amountFromLiability, accountId: liabilityAccount.value.id}] : []),
        ],
        attemptAutoPost: false,
      };

      requests.createTransaction(expenseTransactionsHeaderDraft).then((response) => {
        toast.success('Expense claim transaction created successfully!', {timeout: 5000});

        const expenseTransactionHeaderId = response.data.id;
        requests.postNewExpenseClaim(expenseTransactionHeaderId, notes.value, expenseDate.value, files.value[0]).then((response) => {
          if (response.data) {
            toast.success('Expense claim created successfully!', {timeout: 5000});
            resetExpenseForm();
            liabilityAccount.value = {name: null, id: null};
            assetAccount.value = {name: null, id: null};
            expenseAccount.value = {name: null, id: null};
            fetchAssetAccounts();
            files.value = [];
          } else {
            toast.error('There was an error submitting your expense claim. Please try again.', {timeout: 5000});
          }
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 5000});
        });
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 5000});
      });
    });

    return {
      getRootProps,
      getInputProps,
      fetchAssetAccounts,
      userSelectionOptionsStatic,
      ...rest,
      assetAccounts,
      liabilityAccounts,
      expenseAccounts,
      files,
      projectId,
      projectIdError,
      useAdvance,
      useAdvanceError,
      expenseAccount,
      expenseAccountError,
      liabilityAccount,
      liabilityAccountError,
      assetAccount,
      assetAccountError,
      notes,
      notesError,
      amount,
      amountError,
      expenseDate,
      expenseDateError,
      fileError,
      submitNewExpense,
    };
  },
  data() {
    return {
      projects: [],
    };
  },
  created() {
    this.fetchLiabilityAccounts();
    this.fetchExpenseAccounts();
    this.fetchAssetAccounts();
    this.fetchProjects();
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
    fetchLiabilityAccounts() {
      requests.getAccounts([
        {name: 'types', value: 'liability'},
        {name: 'for_user', value: true},
        {name: 'ui_filters', value: 'expense'}]).then((response) => {
        this.liabilityAccounts = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 5000});
      });
    },
    fetchExpenseAccounts() {
      requests.getAccounts([
        {name: 'types', value: 'expense'},
        {name: 'for_user', value: true},
        {name: 'ui_filters', value: 'expense'},
        ...(this.projectId && this.projectId !== 'null' ? [{name: 'project_id', value: this.projectId}] : []),
      ]).then((response) => {
        this.expenseAccounts = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 5000});
      });
    },
    selectLiabilityAccount(event, i) {
      if (i !== -1) {
        this.liabilityAccount = this.filtered_liability_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectAssetAccount(event, i) {
      if (i !== -1) {
        this.assetAccount = this.filtered_asset_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectExpenseAccount(event, i) {
      if (i !== -1) {
        this.expenseAccount = this.filtered_expense_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    makeAccountLegible(account) {
      return `${account.name}`;
    },

  },
  computed: {
    filtered_liability_account_suggestions() {
      return this.liabilityAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.liabilityAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_asset_account_suggestions() {
      return this.assetAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.assetAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_expense_account_suggestions() {
      return this.expenseAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.expenseAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
  },

};
</script>

<template>
  <div class="grid grid-cols-1">
    <div class="col-span-full">
      <Card title="Submit New Expense">
        <form @submit.prevent="submitNewExpense">
          <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">

            <div class="col-span-6">
              <Select
                :options="projects"
                label="Tag/Project"
                v-model="projectId"
                name="projectId"
                placeholder="Is this for a specific project? If so, select it here."
                :error="projectIdError"
                @change="fetchExpenseAccounts"
              />
            </div>

            <div class="col-span-6">
              <ComboboxTextInput
                :field-model-value="expenseAccount.name"
                :suggestions="filtered_expense_account_suggestions.map(makeAccountLegible)"
                :selected-callback="selectExpenseAccount"
                :allow-new="false"
                :open-by-default="false"
                label="Expense Account"
                type="text"
                placeholder="What kind of expense is this?"
                name="expenseAccount"
                v-model="expenseAccount.name"
                :error="expenseAccountError"
                @change="() => {}"
              />
            </div>

            <div class="col-span-6">
              <TextInput
                  label="Amount (&pound;)"
                  type="text"
                  placeholder="12.34"
                  name="amount"
                  v-model="amount"
                  :error="amountError"
              />
            </div>


            <div class="col-span-6">
              <ComboboxTextInput
                :field-model-value="liabilityAccount.name"
                :suggestions="filtered_liability_account_suggestions.map(makeAccountLegible)"
                :selected-callback="selectLiabilityAccount"
                :allow-new="false"
                :open-by-default="false"
                label="Liability Account"
                type="text"
                placeholder="workshop"
                name="liabilityAccount"
                v-model="liabilityAccount.name"
                :error="liabilityAccountError"
                @change="() => {}"
              />
            </div>

            <div class="col-span-5">
              <Checkbox
                label="Use Advance?"
                name="useAdvance"
                activeClass="ring-primary-500 bg-primary-500"
                v-model="useAdvance"
                :error="useAdvanceError"/>
              <ErrorMessage name="useAdvance" :error="useAdvanceError" class="text-danger-500"/>
            </div>

            <div class="col-span-1">
              <span v-if="assetAccount != null && assetAccount.name" class="text-gray-500">Balance: &#163; {{ (assetAccount.balance / 100).toFixed(2) }}</span>
            </div>

            <div class="col-span-6" >
              <ComboboxTextInput
                v-if="useAdvance"
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


            <div class="col-span-6">
                        <Textarea
                            label="Notes"
                            type="text"
                            placeholder="anything noteworth"
                            name="notes"
                            v-model="notes"
                            :error="notesError"
                        />
            </div>
            <div class="col-span-6 content-center">
              <label class="text-slate-700 dark:text-slate-300">Date of Expense</label>
              <div :class="(expenseDateError ? 'border border-solid border-danger-500 rounded ' : '')">
                <flat-pickr
                    class="form-control m-auto"
                    name="expenseDate"
                    v-model="expenseDate"
                    :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
                >
                </flat-pickr>
              </div>
              <ErrorMessage name="expenseDate" :error="expenseDateError" class="text-danger-500"/>
            </div>
            <div class="col-span-full">
              <div>
                <div
                    v-bind="getRootProps()"
                    :class="'w-full text-center border rounded flex flex-col justify-center items-center '
                    + (fileError ? 'border-danger-500 border-solid' : 'border-secondary-500 border-dashed')
                    "
                >
                  <div v-if="files.length === 0" class="w-full">
                    <input v-bind="getInputProps()" class="hidden" />
                    <img src="@/assets/images/svg/upload.svg" alt="" class="mx-auto mb-4" />
                    <p
                        v-if="isDragActive"
                        class="text-sm text-slate-500 dark:text-slate-300 font-light"
                    >
                      Drop the files here ...
                    </p>
                    <p v-else class="text-sm text-slate-500 dark:text-slate-300 font-light">
                      Drop files here or click to upload.
                    </p>
                  </div>
                  <div v-else class="flex w-full h-full justify-center align-middle">
                    <img
                      v-if="files[0].contentType.startsWith('image/')"
                      :src="files[0].preview"
                      class="object-contain block rounded-md"
                      alt="Receipt photo"
                    />
                    <iframe
                      v-else-if="files[0].contentType === 'application/pdf'"
                      class="w-full h-[500px]"
                      :src="files[0].preview"
                      type="application/pdf"
                    ></iframe>
                  </div>
                </div>
              </div>
              <ErrorMessage name="file" :error="fileError" class="text-danger-500"/>
            </div>
            <div class="col-span-full">
              <Button class="btn block w-full text-center bg-red-700 mb-4" style="text-transform: none;" @click="files = []">
                Clear File(s)
              </Button>
              <Button type="submit" class="btn block w-full text-center">
                Submit
              </Button>
            </div>
          </div>
        </form>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
