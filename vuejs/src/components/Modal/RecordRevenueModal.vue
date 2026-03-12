<script>
import Modal from '@/components/Modal/Modal.vue';
import {useToast} from 'vue-toastification';
import requests from '@/requests';
import {ref} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import Select from '@/components/Select/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import TextInput from '@/components/TextInput/index.vue';
import Button from '@/components/Button/index.vue';
import DashButton from '@/components/Button/index.vue';

const toast = useToast();

export default {
  name: 'RecordRevenueModal',
  components: {DashButton, TextInput, ComboboxTextInput, Select, Modal, Button},
  emits: ['close'],
  setup(props, context) {
    const revenueAccounts = ref([]);
    const assetAccounts = ref([]);
    const projects = ref([]);
    const eventSuggestions = ref([]);

    function getRevenueAccounts() {
      requests.getAccounts([
        {name: 'types', value: 'revenue'},
        {name: 'for_user', value: true},
        {name: 'ui_filters', value: 'transfer'},
        ...(projectId.value && projectId.value !== 'null' ? [{name: 'project_id', value: projectId.value}] : []),
      ]).then((response) => {
        revenueAccounts.value = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    }

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

    const newDonationsSchema = yup.object().shape({
      projectId: yup.string().required(' The project id is required '),
      revenueAccount: yup.object().shape({
        id: yup.string().uuid().required(' The revenue account id is required '),
        name: yup.string().required(' The revenue account name is required '),
      }).required(' The revenue account is required '),

      assetAccount: yup.object().shape({
        id: yup.string().uuid().required(' The asset account id is required '),
        name: yup.string().required(' The asset account name is required '),
      }).required(' The asset account is required '),
      amount: yup.number().required(' The amount is required ').positive(' The amount must be positive '),
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
      validationSchema: newDonationsSchema,
      keepValuesOnUnmount: true,
    });

    const {value: projectId, errorMessage: projectIdError} = useField('projectId');
    const {value: revenueAccount, errorMessage: revenueAccountError} = useField('revenueAccount');
    const {value: assetAccount, errorMessage: assetAccountError} = useField('assetAccount');
    const {value: amount, errorMessage: amountError} = useField('amount');
    const {value: event, errorMessage: eventError} = useField('event');
    const {value: eventNotInList, errorMessage: eventNotInListError} = useField('eventNotInList');

    assetAccount.value = {name: null, id: null};
    revenueAccount.value = {name: null, id: null};
    
    function resetNewDonationsForm() {
      projectId.value = 'null';
      revenueAccount.value = {name: null, id: null};
      assetAccount.value = {name: null, id: null};
      amount.value = null;
      event.value = null;
      eventNotInList.value = false;
    }

    const submitNewDonations = handleSubmit(() => {
      const transactionDraft = {
        transactionHeader: {
          event: event.value,
        },
        transactionLines: [
          {accountId: revenueAccount.value.id, amount: -amount.value * 100},
          {accountId: assetAccount.value.id, amount: amount.value * 100},
        ],
      };

      requests.createTransaction(transactionDraft).then((response) => {
        toast.success('Transaction Created and Posted!', {timeout: 2000});
        resetNewDonationsForm();
        context.emit('close');
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      revenueAccounts,
      assetAccounts,
      revenueAccount,
      assetAccount,
      amount,
      revenueAccountError,
      assetAccountError,
      amountError,
      submitNewDonations,
      getRevenueAccounts,
      getAssetAccounts,
      projectId,
      projectIdError,
      resetNewDonationsForm,
      projects,
      event,
      eventError,
      eventNotInList,
      eventNotInListError,
      eventSuggestions,
    };
  },
  props: {
    activeModal: {
      type: Boolean,
      required: true,
    },
  },
  mounted() {
    this.getRevenueAccounts();
    this.getAssetAccounts();
  },
  methods: {
    closeModal() {
      this.resetNewDonationsForm();
      this.$emit('close');
    },
    selectRevenueAccount(event, i) {
      if (i !== -1) {
        this.revenueAccount = this.filtered_revenue_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectAssetAccount(event, i) {
      if (i !== -1) {
        this.assetAccount = this.filtered_asset_account_suggestions[i];
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
    filtered_revenue_account_suggestions() {
      return this.revenueAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.revenueAccounts.name ?? '').toLowerCase()))
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
    filtered_event_suggestions() {
      return this.eventSuggestions
        .filter((suggestion) => suggestion
          .toLowerCase()
          .startsWith((this.event ?? '').toLowerCase()));
    },
  },
  watch: {
    activeModal(newValue) {
      if (newValue) {
        this.getAssetAccounts();
        this.getRevenueAccounts();
      }
    },
  },
};
</script>

<template>
  <Modal :active-modal="activeModal" @close="closeModal" title="Record Revenue">
    <form @submit.prevent="submitNewDonations">
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-12">
          <Select
            :options="projects"
            label="Tag/Project"
            v-model="projectId"
            name="projectId"
            placeholder="Is this for a specific project? If so, select it here."
            :error="projectIdError"
            @change="() => {getAssetAccounts(); getRevenueAccounts();}"
          />
        </div>
        <div class="col-span-12">
          <ComboboxTextInput
            :field-model-value="revenueAccount.name"
            :suggestions="filtered_revenue_account_suggestions.map(makeAccountLegible)"
            :selected-callback="selectRevenueAccount"
            :allow-new="false"
            :open-by-default="false"
            label="Revenue Account"
            type="text"
            placeholder="What best describes what this revenue is?"
            name="revenueAccount"
            v-model="revenueAccount.name"
            :error="revenueAccountError"
            @change="() => {}"
          />
        </div>
        <div class="col-span-12">
          <ComboboxTextInput
            :field-model-value="assetAccount.name"
            :suggestions="filtered_asset_account_suggestions.map(makeAccountLegible)"
            :selected-callback="selectAssetAccount"
            :allow-new="false"
            :open-by-default="false"
            label="Asset Account"
            type="text"
            placeholder="Where does this revenue go to?"
            name="assetAccount"
            v-model="assetAccount.name"
            :error="assetAccountError"
            @change="() => {}"
          />
        </div>
        <div class="col-span-12">
          <TextInput
            label="Amount (&pound;)"
            type="text"
            placeholder="12.34"
            name="amount"
            v-model="amount"
            :error="amountError"
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
