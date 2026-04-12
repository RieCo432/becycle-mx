<script>
import Modal from '@/components/Modal/Modal.vue';
import DashButton from '@/components/Button/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import Select from '@/components/Select/index.vue';
import Button from '@/components/Button/index.vue';
import {ref} from 'vue';
import requests from '@/requests';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import Checkbox from '@/components/Checkbox/index.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'RecordPayoutModal',
  components: {Checkbox, DashButton, TextInput, ComboboxTextInput, Select, Modal, Button},
  emits: ['close'],
  setup(props, context) {
    const assetAccounts = ref([]);
    const expenseAccounts = ref([]);
    const projects = ref([]);
    const eventSuggestions = ref([]);

    function getAssetAccounts() {
      requests.getAccounts([
        {name: 'types', value: 'asset'},
        {name: 'for_user', value: true},
        {name: 'ui_filters', value: 'transfer'},
        ...(projectId.value && projectId.value !== 'null' ? [{name: 'project_id', value: projectId.value}] : []),
      ]).then((response) => {
        assetAccounts.value = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    }

    function getExpenseAccounts() {
      requests.getAccounts([
        {name: 'types', value: 'expense'},
        {name: 'for_user', value: true},
        {name: 'ui_filters', value: 'transfer'},
        ...(projectId.value && projectId.value !== 'null' ? [{name: 'project_id', value: projectId.value}] : []),
      ]).then((response) => {
        expenseAccounts.value = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    }

    requests.getProjects().then((response) => {
      projects.value = [
        {label: 'No Project', value: 'null'},
        ...response.data.map((t) => (
          {
            label: `${t.id} --- ${t.description}`,
            value: t.id,
          }
        ))];
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });

    requests.getTransactionEvents().then((response) => {
      eventSuggestions.value = response.data;
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });

    const newPayoutSchema = yup.object().shape({
      projectId: yup.string().required(' The project id is required '),
      sourceAssetAccount: yup.object().shape({
        id: yup.string().uuid().required(' The source asset account id is required '),
        name: yup.string().required(' The source asset account name is required '),
      }).required(' The source asset account is required '),

      destinationAssetAccount: yup.object().shape({
        id: yup.string().uuid().required(' The destination asset account id is required '),
        name: yup.string().required(' The destination asset account name is required '),
      }).required(' The destination asset account is required '),
      amountPayout: yup.number().required(' The amount is required ').positive(' The amount must be positive '),
      hasFee: yup.boolean(),
      amountFee: yup.number().when('hasFee', {
        is: true,
        then: (schema) => schema.required(' The amount fee is required ').positive(' The amount fee must be positive '),
        otherwise: (schema) => schema,
      }),
      feeExpenseAccount: yup.object().when('hasFee', {
        is: true,
        then: () => yup.object().shape({
          id: yup.string().uuid().required(' The expense account id is required '),
          name: yup.string().required(' The expense account name is required ')})
          .required('This is required if a fee is paid.'),
        otherwise: () => yup.object().nullable(),
      }),
      event: yup.string().required(' The event is required ')
        .max(60, 'The event must be less than 60 characters')
        .when('eventNotInList', {
          is: true,
          then: (schema) => schema,
          otherwise: (schema) => schema.oneOf(eventSuggestions.value, 'Please choose a value from the list, or add a new event.'),
        }),
      eventNotinList: yup.boolean(),
    });

    const {handleSubmit} = useForm({
      validationSchema: newPayoutSchema,
      keepValuesOnUnmount: true,
    });

    const {value: projectId, errorMessage: projectIdError} = useField('projectId');
    const {value: sourceAssetAccount, errorMessage: sourceAssetAccountError} = useField('sourceAssetAccount');
    const {value: destinationAssetAccount, errorMessage: destinationAssetAccountError} = useField('destinationAssetAccount');
    const {value: amountPayout, errorMessage: amountPayoutError, setErrors: setAmountPayoutErrors} = useField('amountPayout');
    const {value: hasFee, errorMessage: hasFeeError} = useField('hasFee');
    const {value: amountFee, errorMessage: amountFeeError} = useField('amountFee');
    const {value: feeExpenseAccount, errorMessage: feeExpenseAccountError} = useField('feeExpenseAccount');
    const {value: event, errorMessage: eventError} = useField('event');
    const {value: eventNotInList, errorMessage: eventNotInListError} = useField('eventNotInList');

    sourceAssetAccount.value = {name: null, id: null};
    destinationAssetAccount.value = {name: null, id: null};
    feeExpenseAccount.value = {name: null, id: null};

    function resetNewPayoutForm() {
      projectId.value = null;
      sourceAssetAccount.value = {name: null, id: null};
      destinationAssetAccount.value = {name: null, id: null};
      amountPayout.value = null;
      hasFee.value = false;
      amountFee.value = null;
      feeExpenseAccount.value = {name: null, id: null};
      event.value = null;
      eventNotInList.value = false;
    }

    const submitNewPayout = handleSubmit(() => {
      if (amountPayout.value * 100 > sourceAssetAccount.value.balance) {
        setAmountPayoutErrors('Insufficient funds');
        return;
      }
      const transactionDraft = {
        transactionHeader: {
          event: event.value,
        },
        transactionLines: [
          {
            accountId: sourceAssetAccount.value.id,
            amount: -Math.round(amountPayout.value * 100)},
          {
            accountId: destinationAssetAccount.value.id,
            amount: Math.round((amountPayout.value - (hasFee.value ? amountFee.value : 0)) * 100)},
          ...(hasFee.value ?
            [{
              accountId: feeExpenseAccount.value.id,
              amount: Math.round(amountFee.value * 100)}] :
            []),
        ],
        attemptAutoPost: true,
      };

      requests.createTransaction(transactionDraft).then((response) => {
        toast.success('Transaction created successfully', {timeout: 2000});
        resetNewPayoutForm();
        context.emit('close');
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      projects,
      assetAccounts,
      expenseAccounts,
      projectId,
      projectIdError,
      sourceAssetAccount,
      sourceAssetAccountError,
      destinationAssetAccount,
      destinationAssetAccountError,
      amountPayout,
      amountPayoutError,
      hasFee,
      hasFeeError,
      amountFee,
      amountFeeError,
      feeExpenseAccount,
      feeExpenseAccountError,
      event,
      eventError,
      eventNotInList,
      eventNotInListError,
      resetNewPayoutForm,
      submitNewPayout,
      getAssetAccounts,
      getExpenseAccounts,
      eventSuggestions,
    };
  },
  props: {
    activeModal: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    closeModal() {
      this.resetNewPayoutForm();
      this.$emit('close');
    },
    selectSourceAssetAccount(event, i) {
      if (i !== -1) {
        this.sourceAssetAccount = this.filtered_source_asset_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectDestinationAssetAccount(event, i) {
      if (i !== -1) {
        this.destinationAssetAccount = this.filtered_destination_asset_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectFeeExpenseAccount(event, i) {
      if (i !== -1) {
        this.feeExpenseAccount = this.filtered_fee_expense_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectEvent(event, i) {
      if (i !== -1) {
        this.event = this.filtered_event_suggestions[i];
      }
    },
    makeAccountLegible(account) {
      return `${account.name}`;
    },
  },
  computed: {
    filtered_source_asset_account_suggestions() {
      return this.assetAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.sourceAssetAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_destination_asset_account_suggestions() {
      return this.assetAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.destinationAssetAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_fee_expense_account_suggestions() {
      return this.expenseAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.feeExpenseAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_event_suggestions() {
      return this.eventSuggestions
        .filter((suggestion) => suggestion
          .toLowerCase()
          .startsWith((this.event ?? '').toLowerCase()));
    },
  },
  mounted() {
    this.getAssetAccounts();
    this.getExpenseAccounts();
  },
  watch: {
    activeModal(newValue) {
      if (newValue) {
        this.getAssetAccounts();
        this.getExpenseAccounts();
      }
    },
  },
};
</script>

<template>
  <Modal :active-modal="activeModal" @close="closeModal" title="Record Payout">
    <form @submit.prevent="submitNewPayout">
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-12">
          <Select
            :options="projects"
            label="Tag/Project"
            v-model="projectId"
            name="projectId"
            placeholder="Is this for a specific project? If so, select it here."
            :error="projectIdError"
            @change="() => {getAssetAccounts(); getExpenseAccounts();}"
          />
        </div>
        <div class="col-span-12">
          <ComboboxTextInput
            :field-model-value="sourceAssetAccount.name"
            :suggestions="filtered_source_asset_account_suggestions.map(makeAccountLegible)"
            :selected-callback="selectSourceAssetAccount"
            :allow-new="false"
            :open-by-default="false"
            label="Source Asset Account"
            type="text"
            placeholder="Where is the money currently?"
            name="sourceAssetAccount"
            v-model="sourceAssetAccount.name"
            :error="sourceAssetAccountError"
            @change="() => {}"
          />
        </div>
        <div class="col-span-12">
          <span v-if="sourceAssetAccount.id" class="text-danger-500">Balance: &#163; {{ (sourceAssetAccount.balance / 100).toFixed(2) }}</span>
        </div>
        <div class="col-span-12">
          <ComboboxTextInput
            :field-model-value="destinationAssetAccount.name"
            :suggestions="filtered_destination_asset_account_suggestions.map(makeAccountLegible)"
            :selected-callback="selectDestinationAssetAccount"
            :allow-new="false"
            :open-by-default="false"
            label="Destination Asset Account"
            type="text"
            placeholder="Where is the money going to?"
            name="destinationAssetAccount"
            v-model="destinationAssetAccount.name"
            :error="destinationAssetAccountError"
            @change="() => {}"
          />
        </div>
        <div class="col-span-12">
          <TextInput
            label="Amount coming out(&pound;)"
            type="text"
            placeholder="12.34"
            name="amountPayout"
            v-model="amountPayout"
            :error="amountPayoutError"
          />
        </div>
        <div :class="hasFee ? 'col-span-4' : 'col-span-full'">
          <Checkbox
            label="Is there a fee?"
            type="checkbox"
            name="hasFee"
            v-model="hasFee"
            :error="hasFeeError"
          />
        </div>
        <div v-if="hasFee" class="col-span-8">
          <TextInput
            label="Amount Fee(&pound;)"
            type="text"
            placeholder="12.34"
            name="amountFee"
            v-model="amountFee"
            :error="amountFeeError"
          />
        </div>
        <div v-if="hasFee" class="col-span-12">
          <ComboboxTextInput
            :field-model-value="feeExpenseAccount.name"
            :suggestions="filtered_fee_expense_account_suggestions.map(makeAccountLegible)"
            :selected-callback="selectFeeExpenseAccount"
            :allow-new="false"
            :open-by-default="false"
            label="Fee Expense Account"
            type="text"
            placeholder="What account should the fee be paid to?"
            name="feeExpenseAccount"
            v-model="feeExpenseAccount.name"
            :error="feeExpenseAccountError"
            @change="() => {}"
          />
        </div>
        <div class="col-span-8">
          <ComboboxTextInput
            :allow-new="eventNotInList"
            :field-model-value="event"
            :suggestions="filtered_event_suggestions"
            :selected-callback="selectEvent"
            label="Event"
            type="text"
            placeholder="What type of event is this?"
            name="event"
            v-model="event"
            :error="eventError"
          />
        </div>
        <div class="col-span-4">
          <label
            class="flex-0 mr-6 w-[140px] break-words ltr:inline-block rtl:block input-label">
            Add New
          </label>
          <DashButton
            :class="`btn-sm ${eventNotInList ? 'bg-success-500 dark:bg-success-500' : 'bg-primary-500 dark:bg-primary-500'} w-full`"
            :icon="eventNotInList ? 'heroicons-outline:check' : 'heroicons-outline:plus'"
            @click.prevent="() => {eventNotInList = !eventNotInList}"
          />
        </div>
        <div class="col-span-12">
          <Button type="submit" class="btn btn-dark block w-full text-center" text="Submit"/>
        </div>
      </div>
    </form>
  </Modal>
</template>

<style scoped lang="scss">

</style>
