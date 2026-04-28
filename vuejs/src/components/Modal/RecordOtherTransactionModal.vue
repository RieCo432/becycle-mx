<script>
import Button from '@/components/Button/index.vue';
import {nextTick, ref} from 'vue';
import requests from '@/requests';
import * as yup from 'yup';
import {useField, useFieldArray, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';
import DashButton from '@/components/Button/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import Select from '@/components/Select/index.vue';
import Modal from '@/components/Modal/Modal.vue';
import {Icon} from '@iconify/vue';
import {validate} from 'uuid';
import Tooltip from '@/components/Tooltip/index.vue';

const toast = useToast();

export default {
  name: 'RecordOtherTransactionModal',
  components: {Tooltip, Icon, DashButton, TextInput, ComboboxTextInput, Select, Modal, Button},
  emits: ['close'],
  setup(props, context) {
    const allAccounts = ref([]);
    const eventSuggestions = ref([]);
    const allUsers = ref([]);
    const additionalUsernamesThatCanPostToSomeAccount = ref([]);
    const loggedInUsername = ref(null);
    const doesTransactionBalance = ref(true);
    const currentSetOfUsernames = ref([]);

    requests.getTransactionEvents().then((response) => {
      eventSuggestions.value = response.data;
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });

    requests.getUserMe().then((response) => {
      loggedInUsername.value = response.data.username;
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });

    requests.getActiveUsers().then((response) => {
      allUsers.value.splice(0, allUsers.value.length, ...response.data);
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

      canBePostedByCurrentSetOfUsers: yup.boolean()
        .oneOf([true], 'None of the current users can post to this account.'),
    });

    const userAuthSchema = yup.object({
      username: yup.string().required('Username is required'),
      password: yup.string().required('Password is required'),
    });

    const newTransactionSchema = yup.object().shape({
      transactionLines: yup.array()
        .of(transactionLineSchema)
        .min(1, 'Add at least one transaction line')
        .required('Transaction lines are required'),
      usernamesAndPasswords: yup.array()
        .of(userAuthSchema),
      event: yup.string().required(' The event is required ')
        .max(60, 'The event must be less than 60 characters')
        .when('eventNotInList', {
          is: true,
          then: (schema) => schema,
          otherwise: (schema) => schema.oneOf(eventSuggestions.value, 'Please choose a value from the list, or add a new event.'),
        }),
      eventNotinList: yup.boolean(),
    });

    function getBlankTransactionLine() {
      return {
        account: {id: null, name: null},
        type: null,
        amount: null,
        canBePostedByCurrentSetOfUsers: true,
      };
    }

    function getBlankUserAuth() {
      return {
        username: null,
        password: null,
      };
    }


    const {setFieldValue, handleSubmit, errors, validate, setFieldError} = useForm({
      validationSchema: newTransactionSchema,
      keepValuesOnUnmount: false,
      initialValues: {
        transactionLines: [
          getBlankTransactionLine(),
          getBlankTransactionLine(),
        ],
        usernamesAndPasswords: [],
        event: null,
      },
    });


    const {
      fields: transactionLines,
      push: pushTransactionLine,
      remove: removeTransactionLine,
    } = useFieldArray('transactionLines');
    const {
      fields: usernamesAndPasswords,
      push: pushUsernamesAndPasswords,
      remove: removeUsernamesAndPasswords,
    } = useFieldArray('usernamesAndPasswords');
    const {value: event, errorMessage: eventError} = useField('event');
    const {value: eventNotInList, errorMessage: eventNotInListError} = useField('eventNotInList');

    function resetNewTransferForm() {
      let numberTransactionLinesToRemove = transactionLines.value.length;
      while (numberTransactionLinesToRemove > 0) {
        removeTransactionLine(0);
        numberTransactionLinesToRemove--;
      }
      let numberUsernamesAndPasswordsToRemove = usernamesAndPasswords.value.length;
      while (numberUsernamesAndPasswordsToRemove > 0) {
        removeUsernamesAndPasswords(0);
        numberUsernamesAndPasswordsToRemove--;
      }
      for (let i=0; i<2; i++) {
        pushTransactionLine(getBlankTransactionLine());
      }
      event.value = null;
      eventNotInList.value = false;
    }

    const submitNewTransaction = handleSubmit(() => {
      let transactionBalance = 0;

      const transactionDraft = {
        transactionHeader: {
          event: event.value,
        },
        transactionLines: transactionLines.value.map((transactionLine) => {
          const amount = Math.round(transactionLine.value.amount * 100) * (transactionLine.value.type === 'debit' ? 1 : -1);
          transactionBalance += amount;
          return {
            accountId: transactionLine.value.account.id,
            amount: amount,
          };
        }),
        attemptAutoPost: true,
      };
      
      doesTransactionBalance.value = transactionBalance === 0;
      if (!doesTransactionBalance.value) return;

      const additionalData = usernamesAndPasswords.value.map((usernameAndPassword) => ({
        username: usernameAndPassword.value.username,
        password: usernameAndPassword.value.password,
      }));

      requests.createTransaction(transactionDraft, additionalData).then((response) => {
        toast.success('Transaction created and posted successfully', {timeout: 2000});
        resetNewTransferForm();
        context.emit('close');
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });


    return {
      allAccounts,
      removeTransactionLine,
      pushTransactionLine,
      transactionLines,
      removeUsernamesAndPasswords,
      pushUsernamesAndPasswords,
      usernamesAndPasswords,
      errors,
      event,
      eventError,
      eventNotInList,
      eventNotInListError,
      resetNewTransferForm,
      submitNewTransaction,
      getAccounts,
      eventSuggestions,
      allUsers,
      loggedInUsername,
      setFieldValue,
      getBlankTransactionLine,
      additionalUsernamesThatCanPostToSomeAccount,
      getBlankUserAuth,
      validate,
      setFieldError,
      doesTransactionBalance,
      currentSetOfUsernames,
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
    selectAccount(event, selectedIndex, transactionLineIndex) {
      if (selectedIndex !== -1) {
        this.setFieldValue(`transactionLines[${transactionLineIndex}].account.name`,
          this.filtered_account_suggestions[transactionLineIndex][selectedIndex].name);
        this.setFieldValue(`transactionLines[${transactionLineIndex}].account.id`,
          this.filtered_account_suggestions[transactionLineIndex][selectedIndex].id);
        this.userSelectionOptionsStatic = false;

        nextTick(() => this.checkUserPostingRights());
      }
    },

    checkUserPostingRights() {
      this.currentSetOfUsernames = this.usernamesAndPasswords
        .map(
          (usernameAndPassword) => {
            const signingUser = this.allUsers.find(
              (user) =>
                user.username === usernameAndPassword.value?.username);
            if (signingUser) {
              return signingUser.username;
            }
          },
        )
        .filter((username) => username !== undefined && username !== null);

      if (!this.currentSetOfUsernames.includes(this.loggedInUsername)) {
        this.currentSetOfUsernames.push(this.loggedInUsername);
      }

      this.additionalUsernamesThatCanPostToSomeAccount
        .splice(0, this.additionalUsernamesThatCanPostToSomeAccount.length);

      let isCurrentSetOfUsersSufficient = true;

      for (let i=0; i < this.transactionLines.length; i++) {
        const usernamesThatCanPostToThisAccount = [];
        const account = this.allAccounts.find(
          (account) =>
            account.id === this.transactionLines[i].value.account.id);
        if (!account) {
          this.setFieldValue(
            `transactionLines[${i}].canBePostedByCurrentSetOfUsers`, true);
          continue;
        }

        if (account.ownerGroupId) {
          usernamesThatCanPostToThisAccount
            .push(
              ...this.allUsers
                .filter((user) =>
                  user
                    .groups
                    .map((group) => group.id)
                    .includes(account.ownerGroupId))
                .map((user) => user.username));
        }

        if (account.ownerUserId) {
          const ownerUser = this.allUsers.find((user) => user.id === account.ownerUserId);
          if (!usernamesThatCanPostToThisAccount.includes(ownerUser.username)) {
            usernamesThatCanPostToThisAccount
              .push(this.allUsers
                .find((user) => user.id === account.ownerUserId)
                .username,
              );
          }
        }

        usernamesThatCanPostToThisAccount.forEach((username) => {
          if (
            !this.additionalUsernamesThatCanPostToSomeAccount.includes(username) &&
            username !== this.loggedInUsername
          ) {
            this.additionalUsernamesThatCanPostToSomeAccount.push(username);
          }
        });

        let isCurrentSetOfUsersSufficientForThisAccount = false;

        for (let j=0; j<usernamesThatCanPostToThisAccount.length; j++) {
          isCurrentSetOfUsersSufficientForThisAccount |=
            this.currentSetOfUsernames.includes(usernamesThatCanPostToThisAccount[j]);
        }

        this.setFieldValue(
          `transactionLines[${i}].canBePostedByCurrentSetOfUsers`,
          isCurrentSetOfUsersSufficientForThisAccount);
        if (!isCurrentSetOfUsersSufficientForThisAccount) {
          this.setFieldError(
            `transactionLines[${i}].canBePostedByCurrentSetOfUsers`,
            'None of the current users can post to this account.');
        }

        isCurrentSetOfUsersSufficient &= isCurrentSetOfUsersSufficientForThisAccount;
      }

      const amountAdditionalUsersNullOrEmpty = this.usernamesAndPasswords
        .filter((usernameAndPassword) => usernameAndPassword.value.username === null || usernameAndPassword.value.username === '')
        .length;

      if (amountAdditionalUsersNullOrEmpty > 0) {
        let amountToBeDeleted = amountAdditionalUsersNullOrEmpty;
        let i = 0;
        while (amountToBeDeleted > 0 && i < this.usernamesAndPasswords.length) {
          if (this.usernamesAndPasswords[i].value.username === null) {
            this.removeUsernamesAndPasswords(i);
            amountToBeDeleted--;
          } else {
            i++;
          }
        }
      }
      if (!isCurrentSetOfUsersSufficient) {
        this.pushUsernamesAndPasswords(this.getBlankUserAuth());
      }
      nextTick(validate);
    },

    selectEvent(event, i) {
      if (i !== -1) {
        this.event = this.filtered_event_suggestions[i];
      }
    },
    makeAccountLegible(account) {
      return `${account.name}`;
    },
    selectUser(event, selectedIndex, usernameAndPasswordIndex) {
      if (selectedIndex !== -1) {
        this.setFieldValue(`usernamesAndPasswords[${usernameAndPasswordIndex}].username`,
          this.filtered_user_suggestions[usernameAndPasswordIndex][selectedIndex]);
        nextTick(this.checkUserPostingRights);
      }
    },
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
    filtered_user_suggestions() {
      return this.usernamesAndPasswords.map((usernameAndPassword) => (
        this.additionalUsernamesThatCanPostToSomeAccount.filter((suggestion) => suggestion
          .toLowerCase()
          .includes((usernameAndPassword.value.username ?? '').toLowerCase()) &&
          !this.currentSetOfUsernames.includes(suggestion.toLowerCase()))
      ));
    },
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
  <Modal
    :active-modal="activeModal"
    @close="closeModal"
    title="Record Other Transaction"
    size-class="max-w-[1200px]">
    <form @submit.prevent="submitNewTransaction">
      <div class="grid grid-cols-12 gap-5">
        <div
          class="col-span-full ps-2 grid grid-cols-12 rounded-md gap-5 bg-slate-300 dark:bg-slate-700"
          v-for="(transactionLine, index) in transactionLines"
          :key="index">
          <div class="col-span-6 mb-2">
            <ComboboxTextInput
              :field-model-value="transactionLine.value.account.name"
              :suggestions="filtered_account_suggestions[index]
              .map(makeAccountLegible)"
              :selected-callback="(event, i) => selectAccount(event, i, index)"
              :allow-new="false"
              :open-by-default="false"
              label="Account"
              type="text"
              placeholder="Which account?"
              :name="`transactionLines[${index}].account.name`"
              v-model="transactionLine.value.account.name"
              @change="() => {}"
              :error="errors[`transactionLines[${index}].account.name`] ?
              errors[`transactionLines[${index}].account.name`] :
              ''"
            />
          </div>
          <div class="col-span-2">
            <Select
              :options="[
                {value: 'debit', label: 'Debit'},
                {value: 'credit', label: 'Credit'},
                ]"
              label="Debit or Credit?"
              v-model="transactionLine.type"
              :name="`transactionLines[${index}].type`"
              placeholder="Cr/Dr?"
              :error="errors[`transactionLines[${index}].type`] ?
              errors[`transactionLines[${index}].type`] :
              ''"
              @update:modelValue="(newValue) => {
                setFieldValue(`transactionLines[${index}].type`, newValue);
              }"
            />
          </div>
          <div class="col-span-2">
            <TextInput
              label="Amount (&pound;)"
              type="text"
              placeholder="12.34"
              :name="`transactionLines[${index}].amount`"
              v-model="transactionLine.amount"
              :error="errors[`transactionLines[${index}].amount`] ?
              errors[`transactionLines[${index}].amount`] :
              ''"
              @update:modelValue="(newValue) => {
                setFieldValue(`transactionLines[${index}].amount`, newValue);
              }"
            />
          </div>
          <div class="col-span-1 place-items-center">
            <div
              v-if="errors[`transactionLines[${index}].canBePostedByCurrentSetOfUsers`]"
              class="flex items-center justify-center h-full">
              <Tooltip
                placement="top"
                theme="dark"
                arrow>
                <template #button>
                  <Icon
                    class="text-danger-500 dark:text-danger-500  text-5xl"
                    icon="heroicons-outline:shield-exclamation" />
                </template>
                <span>{{ errors[`transactionLines[${index}].canBePostedByCurrentSetOfUsers`] ?? '' }}</span>
              </Tooltip>
            </div>
          </div>
          <div class="col-span-1">
            <Button
              icon="heroicons-outline:trash"
              class="w-full h-full"
              @click="removeTransactionLine(index)"/>
          </div>

        </div>
        <div class="col-span-12">
          <Button
            icon="heroicons-outline:plus"
            class="w-full"
            @click="pushTransactionLine(getBlankTransactionLine())"/>
        </div>
        <div class="col-span-12">
          <Button
            icon="heroicons-outline:magnifying-glass"
            class="w-full"
            @click="checkUserPostingRights"/>
        </div>
        <div class="col-span-12">
          <div
            class="col-span-full px-2 grid grid-cols-12 rounded-md gap-5 bg-slate-300 dark:bg-slate-700"
            v-for="(usernameAndPassword, index) in usernamesAndPasswords"
            :key="index"
          >
            <div class="col-span-6 mb-2">
              <ComboboxTextInput
                :field-model-value="usernameAndPassword.value.username"
                :suggestions="filtered_user_suggestions[index]"
                :selected-callback="(event, i) => selectUser(event, i, index)"
                :allow-new="false"
                :open-by-default="false"
                label="Username"
                type="text"
                placeholder="workshop"
                :name="`usernamesAndPasswords[${index}].username`"
                v-model="usernameAndPassword.value.username"
                :error="errors[`usernamesAndPasswords[${index}].username`] ?
                errors[`usernamesAndPasswords[${index}].username`] :
                ''"
                @change="() => {}"
              />
            </div>
            <div class="col-span-6">
              <TextInput
                label="Password"
                type="password"
                placeholder="Password"
                :name="`usernamesAndPasswords[${index}].password`"
                v-model="usernameAndPassword.value.password"
                :error="errors[`usernamesAndPasswords[${index}].password`] ?
                errors[`usernamesAndPasswords[${index}].password`] :
                ''"
                hasicon/>
            </div>

          </div>
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
            :class="`btn-sm ${eventNotInList ?
            'bg-success-500 dark:bg-success-500' :
            'bg-primary-500 dark:bg-primary-500'} w-full`"
            :icon="eventNotInList ? 'heroicons-outline:check' : 'heroicons-outline:plus'"
            @click.prevent="() => {eventNotInList = !eventNotInList}"
          />
        </div>
        <div v-if="!doesTransactionBalance" class="col-span-12">
          <div
            class="flex items-center justify-center h-full">
            <Tooltip
              placement="top"
              theme="dark"
              arrow>
              <template #button>
                <Icon
                  class="text-danger-500 dark:text-danger-500  text-5xl"
                  icon="heroicons-outline:scale" />
              </template>
              <span>The sum or credits needs to match the sum of debits</span>
            </Tooltip>
          </div>
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
