<script>
import Button from '@/components/Button/index.vue';
import {ref} from 'vue';
import requests from '@/requests';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';
import DashButton from '@/components/Button/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import Select from '@/components/Select/index.vue';
import Modal from '@/components/Modal/Modal.vue';

const toast = useToast();

export default {
  name: 'RecordTransferModal',
  components: {DashButton, TextInput, ComboboxTextInput, Select, Modal, Button},
  emits: ['close'],
  setup(props, context) {
    const creditAccounts = ref([]);
    const debitAccounts = ref([]);
    const projects = ref([]);
    const eventSuggestions = ref([]);

    const creditUsers = ref([]);
    const debitUsers = ref([]);
    const loggedInUser = ref(null);

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

    requests.getUserMe().then((response) => {
      loggedInUser.value = response.data.username;
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });

    function getCreditAccounts() {
      requests.getAccounts([
        {name: 'for_user', value: false},
        {name: 'ui_filters', value: 'transfer'},
        ...(projectId.value && projectId.value !== 'null' ? [{name: 'project_id', value: projectId.value}] : []),
      ]).then((response) => {
        creditAccounts.value = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    }

    function getDebitAccounts() {
      if (creditAccount.value) {
        requests.getAccounts([
          {name: 'types', value: creditAccount.value.type},
          {name: 'for_user', value: false},
          {name: 'ui_filters', value: 'transfer'},
          ...(projectId.value && projectId.value !== 'null' ? [{name: 'project_id', value: projectId.value}] : []),
        ]).then((response) => {
          debitAccounts.value = response.data.filter((account) => account.id !== creditAccount.value.id);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
      }
    }

    const newTransferSchema = yup.object().shape({
      projectId: yup.string().required(' The project id is required '),
      creditAccount: yup.object().shape({
        id: yup.string().uuid().required(' The credit account id is required '),
        name: yup.string().required(' The credit account name is required '),
      }).required(' The credit account is required '),
      loggedInUserCanSignCreditAccount: yup.boolean(),
      creditAccountUsername: yup.string().when('loggedInUserCanSignCreditAccount', {
        is: false,
        then: (schema) => schema.required(' The credit account username is required '),
        otherwise: (schema) => schema.notRequired(),
      }),
      creditAccountPassword: yup.string().when('loggedInUserCanSignCreditAccount', {
        is: false,
        then: (schema) => schema.required(' The credit account password is required '),
        otherwise: (schema) => schema.notRequired(),
      }),

      debitAccount: yup.object().shape({
        id: yup.string().uuid().required(' The debit account id is required '),
        name: yup.string().required(' The debit account name is required '),
      }).required(' The debit account is required '),
      amount: yup.number().required(' The amount is required ').positive(' The amount must be positive '),
      loggedInUserCanSignDebitAccount: yup.boolean(),
      debitAccountUsername: yup.string().when('loggedInUserCanSignDebitAccount', {
        is: false,
        then: (schema) => schema.required(' The debit account username is required '),
        otherwise: (schema) => schema.notRequired(),
      }),
      debitAccountPassword: yup.string().when('loggedInUserCanSignDebitAccount', {
        is: false,
        then: (schema) => schema.required(' The debit account password is required '),
        otherwise: (schema) => schema.notRequired(),
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
      validationSchema: newTransferSchema,
      keepValuesOnUnmount: true,
    });

    const {value: projectId, errorMessage: projectIdError} = useField('projectId');
    const {value: creditAccount, errorMessage: creditAccountError} = useField('creditAccount');
    const {value: loggedInUserCanSignCreditAccount, errorMessage: loggedInUserCanSignCreditAccountError} =
      useField('loggedInUserCanSignCreditAccount');
    const {value: creditAccountUsername, errorMessage: creditAccountUsernameError} = useField('creditAccountUsername');
    const {value: creditAccountPassword, errorMessage: creditAccountPasswordError} = useField('creditAccountPassword');
    const {value: debitAccount, errorMessage: debitAccountError} = useField('debitAccount');
    const {value: loggedInUserCanSignDebitAccount, errorMessage: loggedInUserCanSignDebitAccountError} =
      useField('loggedInUserCanSignDebitAccount');
    const {value: debitAccountUsername, errorMessage: debitAccountUsernameError} = useField('debitAccountUsername');
    const {value: debitAccountPassword, errorMessage: debitAccountPasswordError} = useField('debitAccountPassword');
    const {value: amount, errorMessage: amountError, setErrors: setAmountErrors} = useField('amount');
    const {value: event, errorMessage: eventError} = useField('event');
    const {value: eventNotInList, errorMessage: eventNotInListError} = useField('eventNotInList');

    creditAccount.value = {name: null, id: null};
    debitAccount.value = {name: null, id: null};


    function resetNewTransferForm() {
      projectId.value = null;
      creditAccount.value = {name: null, id: null};
      debitAccount.value = {name: null, id: null};
      amount.value = null;
      event.value = null;
      eventNotInList.value = false;
      loggedInUserCanSignCreditAccount.value = false;
      loggedInUserCanSignDebitAccount.value = false;
      creditAccountUsername.value = null;
      creditAccountPassword.value = null;
      debitAccountUsername.value = null;
      debitAccountPassword.value = null;
    }

    const submitNewTransfer = handleSubmit(() => {
      // if (amount.value * 100 > amount.value.balance) {
      //   setAmountPayoutErrors('Insufficient funds');
      //   return;
      // }
      const transactionDraft = {
        transactionHeader: {
          event: event.value,
        },
        transactionLines: [
          {accountId: creditAccount.value.id, amount: -Math.round(amount.value * 100)},
          {accountId: debitAccount.value.id, amount: Math.round(amount.value * 100)},
        ],
        attemptAutoPost: true,
      };

      const additionalData = [];
      if (!loggedInUserCanSignCreditAccount.value) {
        additionalData.push({username: creditAccountUsername.value, password: creditAccountPassword.value});
      }
      if (!loggedInUserCanSignDebitAccount.value) {
        additionalData.push({username: debitAccountUsername.value, password: debitAccountPassword.value});
      }

      requests.createTransaction(transactionDraft, additionalData).then((response) => {
        toast.success('Transaction created and posted successfully', {timeout: 2000});
        resetNewTransferForm();
        context.emit('close');
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });


    return {
      projects,
      creditAccounts,
      debitAccounts,
      projectId,
      projectIdError,
      creditAccount,
      creditAccountError,
      loggedInUserCanSignCreditAccount,
      loggedInUserCanSignCreditAccountError,
      creditAccountUsername,
      creditAccountUsernameError,
      creditAccountPassword,
      creditAccountPasswordError,
      debitAccount,
      debitAccountError,
      loggedInUserCanSignDebitAccount,
      loggedInUserCanSignDebitAccountError,
      debitAccountUsername,
      debitAccountUsernameError,
      debitAccountPassword,
      debitAccountPasswordError,
      amount,
      amountError,
      event,
      eventError,
      eventNotInList,
      eventNotInListError,
      resetNewTransferForm,
      submitNewTransfer,
      getCreditAccounts,
      getDebitAccounts,
      eventSuggestions,
      creditUsers,
      debitUsers,
      loggedInUser,
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
      this.resetNewTransferForm();
      this.$emit('close');
    },
    selectCreditAccount(event, i) {
      if (i !== -1) {
        this.creditAccount = this.filtered_credit_account_suggestions[i];
        this.userSelectionOptionsStatic = false;

        this.creditUsers.splice(0, this.creditUsers.length);
        const promises = [];
        if (this.creditAccount.ownerGroupId) {
          promises.push(requests.getGroupUsers(this.creditAccount.ownerGroupId));
        }
        if (this.creditAccount.ownerUserId && !this.creditUsers.find((user) => user.id === this.creditAccount.ownerUser.username)) {
          promises.push(requests.getUser(this.creditAccount.ownerUserId));
        }
        Promise.all(promises).then((responses) => {
          responses.forEach((response) => {
            if (!response.data.length) {
              if (!this.creditUsers.includes(response.data.username)) this.creditUsers.push(response.data.username);
            } else {
              response.data.forEach((user) => {
                if (!this.creditUsers.includes(user.username)) this.creditUsers.push(user.username);
              });
            }
          });
          this.loggedInUserCanSignCreditAccount = this.creditUsers.includes(this.loggedInUser);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
      }
    },
    selectDebitAccount(event, i) {
      if (i !== -1) {
        this.debitAccount = this.filtered_debit_account_suggestions[i];
        this.userSelectionOptionsStatic = false;

        this.debitUsers.splice(0, this.debitUsers.length);
        const promises = [];

        if (this.debitAccount.ownerGroupId) {
          promises.push(requests.getGroupUsers(this.debitAccount.ownerGroupId));
        }
        if (this.debitAccount.ownerUserId && !this.debitUsers.find((user) => user.id === this.debitAccount.ownerUser.username)) {
          promises.push(requests.getUser(this.debitAccount.ownerUserId));
        }
        Promise.all(promises).then((responses) => {
          responses.forEach((response) => {
            if (!response.data.length) {
              if (!this.debitUsers.includes(response.data.username)) this.debitUsers.push(response.data.username);
            } else {
              response.data.forEach((user) => {
                if (!this.debitUsers.includes(user.username)) this.debitUsers.push(user.username);
              });
            }
          });
          this.loggedInUserCanSignDebitAccount = this.debitUsers.includes(this.loggedInUser);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
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
    selectCreditUser(event, i) {
      if (i !== -1) {
        this.creditAccountUsername = this.filtered_credit_user_suggestions[i];
      }
    },
    selectDebitUser(event, i) {
      if (i !== -1) {
        this.debitAccountUsername = this.filtered_debit_user_suggestions[i];
      }
    },
  },
  computed: {
    filtered_credit_account_suggestions() {
      return this.creditAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .includes((this.creditAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 20);
    },
    filtered_debit_account_suggestions() {
      return this.debitAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .includes((this.debitAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_event_suggestions() {
      return this.eventSuggestions
        .filter((suggestion) => suggestion
          .toLowerCase()
          .includes((this.event ?? '').toLowerCase()));
    },
    filtered_credit_user_suggestions() {
      return this.creditUsers
        .filter((suggestion) =>
          suggestion
            .toLowerCase()
            .startsWith((this.creditAccountUsername ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_debit_user_suggestions() {
      return this.debitUsers
        .filter((suggestion) =>
          suggestion
            .toLowerCase()
            .startsWith((this.debitAccountUsername ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
  },
  mounted() {
    this.getCreditAccounts();
  },
  watch: {
    activeModal(newValue) {
      if (newValue) {
        this.getCreditAccounts();
      }
    },
    creditAccount() {
      this.getDebitAccounts();
    },
  },
};
</script>

<template>
  <Modal :active-modal="activeModal" @close="closeModal" title="Record Transfer">
    <form @submit.prevent="submitNewTransfer">
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-12">
          <Select
            :options="projects"
            label="Tag/Project"
            v-model="projectId"
            name="projectId"
            placeholder="Is this for a specific project? If so, select it here."
            :error="projectIdError"
            @change="getCreditAccounts"
          />
        </div>
        <div class="col-span-12">
          <ComboboxTextInput
            :field-model-value="creditAccount.name"
            :suggestions="filtered_credit_account_suggestions.map(makeAccountLegible)"
            :selected-callback="selectCreditAccount"
            :allow-new="false"
            :open-by-default="false"
            label="Credit Account"
            type="text"
            placeholder="Which account is credited?"
            name="creditAccount"
            v-model="creditAccount.name"
            :error="creditAccountError"
            @change="() => {}"
          />
        </div>
        <div class="col-span-12">
          <span v-if="creditAccount.id" class="text-danger-500">Balance: &#163; {{ (creditAccount.balance / 100).toFixed(2) }}</span>
        </div>
        <div v-if="!loggedInUserCanSignCreditAccount && creditAccount.id" class="col-span-6">
          <ComboboxTextInput
            :field-model-value="creditAccountUsername"
            :suggestions="filtered_credit_user_suggestions"
            :selected-callback="selectCreditUser"
            :allow-new="false"
            :open-by-default="false"
            label="Credit Account Username"
            type="text"
            placeholder="workshop"
            name="creditAccountUsername"
            v-model="creditAccountUsername"
            :error="creditAccountUsernameError"
            @change="() => {}"
          />
        </div>
        <div v-if="!loggedInUserCanSignCreditAccount && creditAccount.id" class="col-span-6">
          <TextInput
            label="Credit Account Password"
            type="password"
            placeholder="Password"
            name="creditAccountPassword"
            v-model="creditAccountPassword"
            :error="creditAccountPasswordError"
            hasicon/>
        </div>
        <div class="col-span-12">
          <ComboboxTextInput
            :field-model-value="debitAccount.name"
            :suggestions="filtered_debit_account_suggestions.map(makeAccountLegible)"
            :selected-callback="selectDebitAccount"
            :allow-new="false"
            :open-by-default="false"
            label="Debit Account"
            type="text"
            placeholder="Which account is debited?"
            name="debitAccount"
            v-model="debitAccount.name"
            :error="debitAccountError"
            @change="() => {}"
          />
        </div>
        <div v-if="!loggedInUserCanSignDebitAccount && debitAccount.id" class="col-span-6">
          <ComboboxTextInput
            :field-model-value="debitAccountUsername"
            :suggestions="filtered_debit_user_suggestions"
            :selected-callback="selectDebitUser"
            :allow-new="false"
            :open-by-default="false"
            label="Debit Account Username"
            type="text"
            placeholder="workshop"
            name="debitAccountUsername"
            v-model="debitAccountUsername"
            :error="debitAccountUsernameError"
            @change="() => {}"
          />
        </div>
        <div v-if="!loggedInUserCanSignDebitAccount && debitAccount.id" class="col-span-6">
          <TextInput
            label="Debit Account Password"
            type="password"
            placeholder="Password"
            name="debitAccountPassword"
            v-model="debitAccountPassword"
            :error="debitAccountPasswordError"
            hasicon/>
        </div>
        <div class="col-span-12">
          <TextInput
            label="Amount coming out(&pound;)"
            type="text"
            placeholder="12.34"
            name="amountPayout"
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
