<script setup>

import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import TextInput from '@/components/TextInput/index.vue';
import FormStepNavigation from '@/components/Forms/FormStepNavigation.vue';
import {useToast} from 'vue-toastification';
import {ref, computed} from 'vue';
import * as yup from 'yup';
import requests from '@/requests';
import {useField, useForm} from 'vee-validate';

const toast = useToast();

const emit = defineEmits(['goBack', 'update:draft']);
const props = defineProps({
  draft: {
    type: Object,
    required: true,
  },
});

const processingSubmit = ref(false);
function checkCurrentlyProcessing() {
  if (processingSubmit.value) {
    toast.warning('Please wait for the previous action to complete');
    return true;
  }
  return false;
}

const depositLiabilityAccounts = ref([]);
const depositAssetAccounts = ref([]);

requests.getAccounts([{name: 'types', value: 'liability'}, {name: 'ui_filters', value: 'deposit'}]).then((response) => {
  depositLiabilityAccounts.value = response.data;
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 5000});
});

requests.getAccounts([{name: 'types', value: 'asset'}, {name: 'ui_filters', value: 'deposit'}]).then((response) => {
  depositAssetAccounts.value = response.data;
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 5000});
});

const depositCollectionSchema = yup.object().shape({
  depositAmountCollected: yup.number().min(0, 'Must not be negative').integer().required(' Deposit Amount is required '),
  depositCollectedLiabilityAccount: yup.object().shape({
    id: yup.string().uuid().required(' The deposit liability account id is required '),
    name: yup.string().required(' The deposit liability account name is required '),
  }).required(' The deposit liability account is required '),
  depositCollectedAssetAccount: yup.object().shape({
    id: yup.string().uuid().required(' The deposit asset account id is required '),
    name: yup.string().required(' The deposit asset account name is required '),
  }).required(' The deposit asset account is required '),
  depositCollectingPassword: yup.string().required(),
});


const {handleSubmit} = useForm({
  validationSchema: depositCollectionSchema,
  keepValuesOnUnmount: true,
});

const {value: depositAmountCollected, errorMessage: depositAmountCollectedError} = useField('depositAmountCollected');
const {
  value: depositCollectedLiabilityAccount,
  errorMessage: depositCollectedLiabilityAccountError,
} = useField('depositCollectedLiabilityAccount');
const {
  value: depositCollectedAssetAccount,
  errorMessage: depositCollectedAssetAccountError,
} = useField('depositCollectedAssetAccount');
const {value: depositCollectingPassword, errorMessage: depositCollectingPasswordError,
  setErrors: depositCollectingPasswordSetErrors} = useField('depositCollectingPassword');

const depositCollectedTransactionHeader = ref({});
depositCollectedAssetAccount.value = {name: null, id: null};
depositCollectedLiabilityAccount.value = {name: null, id: null};


function selectDepositCollectedLiabilityAccount(event, i) {
  if (i !== -1) {
    depositCollectedLiabilityAccount.value = filteredDepositCollectedLiabilityAccountSuggestions.value[i];
  }
}

function selectDepositCollectedAssetAccount(event, i) {
  if (i !== -1) {
    depositCollectedAssetAccount.value = filteredDepositCollectedAssetAccountSuggestions.value[i];
  }
}
function makeAccountLegible(account) {
  return `${account.name}`;
}

const submit = handleSubmit(() => {
  if (checkCurrentlyProcessing()) return;
  processingSubmit.value = true;


  if (props.draft.depositCollectedTransactionHeaderId === null) {
    const depositCollectedTransactionDraft = {
      transactionHeader: {
        event: 'deposit_collected',
      },
      transactionLines: [
        {amount: -Math.round(depositAmountCollected.value * 100), accountId: depositCollectedLiabilityAccount.value.id},
        {amount: Math.round(depositAmountCollected.value * 100), accountId: depositCollectedAssetAccount.value.id},
      ],
      attemptAutoPost: true,
    };
    const transactionAuthDetails = [{
      username: depositCollectedAssetAccount.value.ownerUser.username,
      password: depositCollectingPassword.value,
    }];
    requests.createTransaction(depositCollectedTransactionDraft, transactionAuthDetails).then((response) => {
      depositCollectedTransactionHeader.value = response.data;

      toast.success('Deposit Collected!', {timeout: 1000});
      requests.putDraftContractDeposit(
        props.draft.id,
        depositCollectedTransactionHeader.value.id,
        depositCollectedAssetAccount.value.ownerUser.username,
        depositCollectingPassword.value)
        .then((response) => {
          toast.success('Deposit Details Updated!', {timeout: 5000});
          emit('update:draft', response.data);
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 5000});
          if (error.response.status === 400) {
            depositCollectingPasswordSetErrors('Wrong Password!');
          }
        })
        .finally(() => {
          processingSubmit.value = false;
        })
      ;
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 5000});
      if (
        error.response.status === 400 &&
        (error.response.data.detail.username ?? '') === depositCollectedAssetAccount.value.ownerUser.username) {
        depositCollectingPasswordSetErrors('Wrong Password!');
      }
      processingSubmit.value = false;
    });
  } else {
    toast.success('Deposit Details Already Done!', {timeout: 5000});
    processingSubmit.value = false;
    emit('update:draft', props.draft);
  }
});

function goBack() {
  if (checkCurrentlyProcessing()) return;
  emit('goBack');
}

const filteredDepositCollectedLiabilityAccountSuggestions = computed(() => {
  return depositLiabilityAccounts.value
    .filter((suggestion) => suggestion.name
      .toLowerCase()
      .startsWith((depositCollectedLiabilityAccount.value.name ?? '').toLowerCase()))
    // .sort(this.userSortingFunction)
    .slice(0, 10);
});

const filteredDepositCollectedAssetAccountSuggestions = computed(() => {
  return depositAssetAccounts.value
    .filter((suggestion) => suggestion.name
      .toLowerCase()
      .startsWith((depositCollectedAssetAccount.value.name ?? '').toLowerCase()))
    // .sort(this.userSortingFunction)
    .slice(0, 10);
});
</script>

<template>
  <form
    @submit.prevent="() => {
      if (!props.draft.depositCollectedTransactionHeaderId) {
        submit();
      } else {
        emit('update:draft', props.draft)
      }
    }"
    @keydown.enter="() => {}">
    <div class="grid 2xl:grid-cols-4 md:grid-cols-2 grid-cols-1 gap-5">
      <div class="col-span-full">
        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
          Deposit Collection
        </h4>
      </div>
      <div
        v-if="props.draft.depositCollectedTransactionHeaderId"
        class="col-span-full">
        <h5 class="text-danger-500 dark:text-danger-500">
          Deposit has already been collected. This step is read-only.
        </h5>
      </div>
      <TextInput
        label="Deposit Amount (&pound;)"
        type="number"
        placeholder="40"
        name="depositAmountCollected"
        v-model="depositAmountCollected"
        :error="depositAmountCollectedError"
        :is-readonly="props.draft.depositCollectedTransactionHeaderId !== null"
      />

      <ComboboxTextInput
        :field-model-value="depositCollectedLiabilityAccount.name"
        :suggestions="props.draft.depositCollectedTransactionHeaderId === null
                          ? filteredDepositCollectedLiabilityAccountSuggestions.map(makeAccountLegible)
                          : []"
        :selected-callback="selectDepositCollectedLiabilityAccount"
        :allow-new="false"
        label="Liability Account"
        type="text"
        placeholder="workshop"
        name="depositCollectedLiabilityAccount"
        v-model="depositCollectedLiabilityAccount.name"
        :error="depositCollectedLiabilityAccountError"
        @change="() => {}"
        :is-readonly="props.draft.depositCollectedTransactionHeaderId !== null"
      />

      <ComboboxTextInput
        :field-model-value="depositCollectedAssetAccount.name"
        :suggestions="props.draft.depositCollectedTransactionHeaderId === null
                        ? filteredDepositCollectedAssetAccountSuggestions.map(makeAccountLegible)
                        : []"
        :selected-callback="selectDepositCollectedAssetAccount"
        :allow-new="false"
        label="Asset Account"
        type="text"
        placeholder="workshop"
        name="depositCollectedAssetAccount"
        v-model="depositCollectedAssetAccount.name"
        :error="depositCollectedAssetAccountError"
        @change="() => {}"
        :is-readonly="props.draft.depositCollectedTransactionHeaderId !== null"
      />

      <TextInput
        label="Deposit Collector Password"
        type="password"
        placeholder="Password"
        name="depositCollectingPassword"
        v-model="depositCollectingPassword"
        :error="depositCollectingPasswordError"
        :is-readonly="props.draft.depositCollectedTransactionHeaderId !== null"
        hasicon/>
      <div class="col-span-full">
        <FormStepNavigation
          :processing-submit="processingSubmit"
          :submit="submit"
          :go-back="goBack"/>
      </div>
    </div>
  </form>
</template>

<style scoped lang="scss">

</style>
