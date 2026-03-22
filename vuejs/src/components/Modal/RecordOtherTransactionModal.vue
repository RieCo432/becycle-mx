<script>
import Button from '@/components/Button/index.vue';
import {ref} from 'vue';
import requests from '@/requests';
import * as yup from 'yup';
import {useField, useFieldArray, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';
import DashButton from '@/components/Button/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import Select from '@/components/Select/index.vue';
import Modal from '@/components/Modal/Modal.vue';

const toast = useToast();

export default {
  name: 'RecordOtherTransactionModal',
  components: {DashButton, TextInput, ComboboxTextInput, Select, Modal, Button},
  emits: ['close'],
  setup(props, context) {
    const allAccounts = ref([]);

    const eventSuggestions = ref([]);

    const users = ref([]);

    const loggedInUser = ref(null);


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

    function getAccounts() {
      requests.getAccounts([
        {name: 'for_user', value: false},
      ]).then((response) => {
        allAccounts.value = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    }

    const transactionLineSchema = yup.object({
      account: yup.object({
        id: yup.string().uuid().required('Account is required'),
        name: yup.string().required('Account name is required'),
      }).required('Account is required'),

      type: yup.string()
        .oneOf(['debit', 'credit'], 'Choose debit or credit')
        .required('Type is required'),

      amount: yup.number()
        .typeError('Amount must be a number')
        .positive('Amount must be positive')
        .required('Amount is required'),
    });

    const newTransactionSchema = yup.object().shape({
      transactionLines: yup.array()
        .of(transactionLineSchema)
        .min(1, 'Add at least one transaction line')
        .required('Transaction lines are required'),
      event: yup.string().required(' The event is required ')
        .max(60, 'The event must be less than 60 characters')
        .when('eventNotInList', {
          is: true,
          then: (schema) => schema,
          otherwise: (schema) => schema.oneOf(eventSuggestions.value, 'Please choose a value from the list, or add a new event.'),
        }),
      eventNotinList: yup.boolean(),


      // TODO: bind this logic in
      // loggedInUserCanSignDebitAccount: yup.boolean(),
      // debitAccountUsername: yup.string().when('loggedInUserCanSignDebitAccount', {
      //   is: false,
      //   then: (schema) => schema.required(' The debit account username is required '),
      //   otherwise: (schema) => schema.notRequired(),
      // }),
      // debitAccountPassword: yup.string().when('loggedInUserCanSignDebitAccount', {
      //   is: false,
      //   then: (schema) => schema.required(' The debit account password is required '),
      //   otherwise: (schema) => schema.notRequired(),
      // }),
    });

    function getBlankTransactionLine() {
      return {
        account: {id: null, name: null},
        type: null,
        amount: null,
      };
    }


    const {setFieldValue, handleSubmit, errors} = useForm({
      validationSchema: newTransactionSchema,
      keepValuesOnUnmount: true,
      initialValues: {
        transactionLines: [
          getBlankTransactionLine(),
          getBlankTransactionLine(),
        ],
        event: null,
      },
    });


    const {fields: transactionLines, push, remove} = useFieldArray('transactionLines');
    const {value: event, errorMessage: eventError} = useField('event');
    const {value: eventNotInList, errorMessage: eventNotInListError} = useField('eventNotInList');


    function resetNewTransferForm() {
      for (let i=0; i<transactionLines.value.length; i++) {
        remove(i);
      }
      for (let i=0; i<2; i++) {
        push(getBlankTransactionLine());
      }
      event.value = null;
      eventNotInList.value = false;
    }

    const submitNewTransaction = handleSubmit(() => {
      // if (amount.value * 100 > amount.value.balance) {
      //   setAmountPayoutErrors('Insufficient funds');
      //   return;
      // }
      // const transactionDraft = {
      //   transactionHeader: {
      //     event: event.value,
      //   },
      //   transactionLines: [
      //     {accountId: creditAccount.value.id, amount: -amount.value * 100},
      //     {accountId: debitAccount.value.id, amount: amount.value * 100},
      //   ],
      //   attemptAutoPost: false,
      // };
      //
      // const additionalData = [];
      // if (!loggedInUserCanSignCreditAccount.value) {
      //   additionalData.push({username: creditAccountUsername.value, password: creditAccountPassword.value});
      // }
      // if (!loggedInUserCanSignDebitAccount.value) {
      //   additionalData.push({username: debitAccountUsername.value, password: debitAccountPassword.value});
      // }
      //
      // requests.createTransaction(transactionDraft).then((response) => {
      //   toast.success('Transaction created successfully', {timeout: 2000});
      //   requests.postTransaction(response.data.id, additionalData).then((response) => {
      //     toast.success('Transaction posted successfully', {timeout: 2000});
      //     resetNewTransferForm();
      //     context.emit('close');
      //   }).catch((error) => {
      //     toast.error(error.response.data.detail.description, {timeout: 2000});
      //   });
      // }).catch((error) => {
      //   toast.error(error.response.data.detail.description, {timeout: 2000});
      // });
    });


    return {
      allAccounts,
      remove,
      push,
      transactionLines,
      errors,
      event,
      eventError,
      eventNotInList,
      eventNotInListError,
      resetNewTransferForm,
      submitNewTransaction,
      getAccounts,
      eventSuggestions,
      users,
      loggedInUser,
      setFieldValue,
      getBlankTransactionLine,
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
    selectCreditAccount(event, selectedIndex, transactionLineIndex) {
      if (selectedIndex !== -1) {
        this.setFieldValue(`transactionLines[${transactionLineIndex}].account.name`,
          this.filtered_account_suggestions[transactionLineIndex][selectedIndex].name);
        this.setFieldValue(`transactionLines[${transactionLineIndex}].account.id`,
          this.filtered_account_suggestions[transactionLineIndex][selectedIndex].id);
        this.userSelectionOptionsStatic = false;

        // TODO: this logic needs wired in
        // this.creditUsers.splice(0, this.creditUsers.length);
        // const promises = [];
        // if (this.creditAccount.ownerGroupId) {
        //   promises.push(requests.getGroupUsers(this.creditAccount.ownerGroupId));
        // }
        // if (this.creditAccount.ownerUserId && !this.creditUsers.find((user) => user.id === this.creditAccount.ownerUser.username)) {
        //   promises.push(requests.getUser(this.creditAccount.ownerUserId));
        // }
        // Promise.all(promises).then((responses) => {
        //   responses.forEach((response) => {
        //     if (!response.data.length) {
        //       if (!this.creditUsers.includes(response.data.username)) this.creditUsers.push(response.data.username);
        //     } else {
        //       response.data.forEach((user) => {
        //         if (!this.creditUsers.includes(user.username)) this.creditUsers.push(user.username);
        //       });
        //     }
        //   });
        //   this.loggedInUserCanSignCreditAccount = this.creditUsers.includes(this.loggedInUser);
        // }).catch((error) => {
        //   toast.error(error.response.data.detail.description, {timeout: 2000});
        // });
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
    // TODO: more auth logic
    // selectCreditUser(event, i) {
    //   if (i !== -1) {
    //     this.creditAccountUsername = this.filtered_credit_user_suggestions[i];
    //   }
    // },
  },
  computed: {
    filtered_account_suggestions() {
      return this.transactionLines.map((transactionLine) => (
        this.allAccounts.filter((suggestion) => suggestion.name
          .toLowerCase()
          .includes((transactionLine.value.account?.name ?? '').toLowerCase()),
        )
      ));
    },
    filtered_event_suggestions() {
      return this.eventSuggestions
        .filter((suggestion) => suggestion
          .toLowerCase()
          .includes((this.event ?? '').toLowerCase()));
    },
    // TODO: wire in the auth logic
    // filtered_credit_user_suggestions() {
    //   return this.creditUsers
    //     .filter((suggestion) =>
    //       suggestion
    //         .toLowerCase()
    //         .startsWith((this.creditAccountUsername ?? '').toLowerCase()))
    //     // .sort(this.userSortingFunction)
    //     .slice(0, 10);
    // },
  },
  mounted() {
    this.getAccounts();
  },
  watch: {
    activeModal(newValue) {
      if (newValue) {
        this.getAccounts();
        this.resetNewTransferForm();
      }
    },
  },
};
</script>

<template>
  <Modal :active-modal="activeModal" @close="closeModal" title="Record Other Transaction" size-class="max-w-[1200px]">
    <form @submit.prevent="submitNewTransaction">
      <div class="grid grid-cols-12 gap-5">
        <div
          class="col-span-full ps-2 grid grid-cols-12 rounded-md gap-5 bg-slate-300 dark:bg-slate-700"
          v-for="(transactionLine, index) in transactionLines"
          :key="index">
          <div class="col-span-6 mb-2">
            <ComboboxTextInput
              :field-model-value="transactionLine.value.account.name"
              :suggestions="filtered_account_suggestions[index].map(makeAccountLegible)"
              :selected-callback="(event, i) => selectCreditAccount(event, i, index)"
              :allow-new="false"
              :open-by-default="false"
              label="Account"
              type="text"
              placeholder="Which account?"
              :name="`transactionLines[${index}].account.name`"
              v-model="transactionLine.value.account.name"
              @change="() => {}"
              :error="errors[`transactionLines[${index}].account.name`] ? errors[`transactionLines[${index}].account.name`] : ''"
            />
          </div>
          <div class="col-span-3">
            <Select
              :options="[{value: 'debit', label: 'Debit'}, {value: 'credit', label: 'Credit'}]"
              label="Debit or Credit?"
              v-model="transactionLine.type"
              :name="`transactionLines[${index}].type`"
              placeholder="Cr/Dr?"
              :error="errors[`transactionLines[${index}].type`] ? errors[`transactionLines[${index}].type`] : ''"
              @update:modelValue="(newValue) => {setFieldValue(`transactionLines[${index}].type`, newValue);}"
            />
          </div>
          <div class="col-span-2">
            <TextInput
              label="Amount (&pound;)"
              type="text"
              placeholder="12.34"
              :name="`transactionLines[${index}].amount`"
              v-model="transactionLine.amount"
              :error="errors[`transactionLines[${index}].amount`] ? errors[`transactionLines[${index}].amount`] : ''"
              @update:modelValue="(newValue) => {setFieldValue(`transactionLines[${index}].amount`, newValue);}"
            />
          </div>
          <div class="col-span-1">
            <Button icon="heroicons-outline:trash" class="w-full h-full" @click="remove(index)"/>
          </div>

        </div>
        <div class="col-span-12">
          <Button icon="heroicons-outline:plus" class="w-full" @click="push(getBlankTransactionLine())"/>
        </div>

        <!-- TODO: Can this be wired in such that number of users and passwords can be kept as small as possible?-->

        <!--        <div v-if="!loggedInUserCanSignCreditAccount && creditAccount.id" class="col-span-6">-->
        <!--          <ComboboxTextInput-->
        <!--            :field-model-value="creditAccountUsername"-->
        <!--            :suggestions="filtered_credit_user_suggestions"-->
        <!--            :selected-callback="selectCreditUser"-->
        <!--            :allow-new="false"-->
        <!--            :open-by-default="false"-->
        <!--            label="Credit Account Username"-->
        <!--            type="text"-->
        <!--            placeholder="workshop"-->
        <!--            name="creditAccountUsername"-->
        <!--            v-model="creditAccountUsername"-->
        <!--            :error="creditAccountUsernameError"-->
        <!--            @change="() => {}"-->
        <!--          />-->
        <!--        </div>-->
        <!--        <div v-if="!loggedInUserCanSignCreditAccount && creditAccount.id" class="col-span-6">-->
        <!--          <TextInput-->
        <!--            label="Credit Account Password"-->
        <!--            type="password"-->
        <!--            placeholder="Password"-->
        <!--            name="creditAccountPassword"-->
        <!--            v-model="creditAccountPassword"-->
        <!--            :error="creditAccountPasswordError"-->
        <!--            hasicon/>-->
        <!--        </div>-->

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
