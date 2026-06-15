<script setup>
import {ref, computed, watch, onMounted} from 'vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import TextInput from '@/components/TextInput/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import {debounce} from 'lodash-es';
import levenshtein from '@/util/levenshtein';
import FormStepNavigation from '@/components/Forms/FormStepNavigation.vue';
import {useToast} from 'vue-toastification';

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

const clientSchema = yup.object().shape({
  firstName: yup.string().required('First name is required'),
  lastName: yup.string().required('Last name is required'),
  emailAddress: yup
    .string()
    .email('Email is not valid')
    .required('Email is required'),
  confirmEmailAddress: yup
    .string()
    .email('Email is not valid')
    .required('Confirm Email is required')
    .oneOf([yup.ref('emailAddress')], 'Email Addresses must match'),
});

const {handleSubmit} = useForm({
  validationSchema: clientSchema,
  keepValuesOnUnmount: true,
});

const {value: emailAddress, errorMessage: emailAddressError} = useField('emailAddress');
const {value: confirmEmailAddress, errorMessage: confirmEmailAddressError} = useField('confirmEmailAddress');
const {value: firstName, errorMessage: firstNameError} = useField('firstName');
const {value: lastName, errorMessage: lastNameError} = useField('lastName');


const submit = handleSubmit(() => {
  if (checkCurrentlyProcessing()) return;
  processingSubmit.value = true;

  requests.getClientByEmail(emailAddress.value)
    .then((response) => {
      setDraftClient(response.data[0]);
    })
    .catch((error) => {
      if (error.response.status === 404) {
        requests.postNewClient({
          firstName: firstName.value,
          lastName: lastName.value,
          emailAddress: emailAddress.value,
        }).then((response) => {
          toast.success('New Client Created!', {timeout: 1000});
          setDraftClient(response.data);
        });
      }
    });
});


onMounted(() => {
  if (props.draft.client) {
    emailAddress.value = props.draft.client.emailAddress;
    confirmEmailAddress.value = props.draft.client.emailAddress;
    firstName.value = props.draft.client.firstName;
    lastName.value = props.draft.client.lastName;
  }
});

watch(props.draft, async (newValue, oldValue) => {
  firstName.value = newValue.client.firstName;
  lastName.value = newValue.client.lastName;
  emailAddress.value = newValue.client.emailAddress;
  confirmEmailAddress.value = newValue.client.emailAddress;
});

const clientSuggestions = ref([]);
const filteredClientSuggestions = ref([]);


function selectClientFromSuggestions(event, i) {
  const draft = props.draft;
  if (i === -1) {
    draft.client = {id: null, firstName: firstName.value, lastName: lastName.value, emailAddress: emailAddress.value};
  } else {
    draft.client = filteredClientSuggestions.value[i];
  }
  emit('update:draft', draft);
}

function setDraftClient(client) {
  requests.putDraftContractClient(props.draft.id, client.id)
    .then((response) => {
      emit('update:draft', response.data);
      toast.success('Client updated', {timeout: 5000});
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 5000});
    })
    .finally(() => {
      processingSubmit.value = false;
    });
}

async function runFilter() {
  const client = {
    firstName: firstName.value ? firstName.value : '',
    lastName: lastName.value ? lastName.value : '',
    emailAddress: emailAddress.value ? emailAddress.value : '',
  };
  levenshtein.filterSortObject(clientSuggestions.value, client, 4).then((result) => {
    filteredClientSuggestions.value = result;
  });
}

const fetchClientSuggestionsDebounced = debounce(() => {
  if ((
    (firstName.value ? firstName.value.length : 0) +
    (lastName.value ? lastName.value.length : 0) +
    (emailAddress.value ? emailAddress.value.length : 0)
  ) > 2) {
    requests.findClient(
      firstName.value ? firstName.value.toLowerCase() : '',
      lastName.value ? lastName.value.toLowerCase() : '',
      emailAddress.value ? emailAddress.value.toLowerCase() :'',
      5)
      .then((response) => {
        clientSuggestions.value = response.data;
        runFilter();
      });
  }
}, 500, {leading: false, trailing: true});

function resetClientComboBoxes() {
  filteredClientSuggestions.value = [];
  const draft = props.draft;
  draft.client = {firstName: '', lastName: '', emailAddress: ''};
  emit('update:draft', draft);
}

const filteredClientSuggestionsLegible = computed(() => {
  return filteredClientSuggestions.value.map((client) => (`${client.firstName} ${client.lastName} ${client.emailAddress}`));
});


function goBack() {
  if (checkCurrentlyProcessing()) return;
  emit('goBack');
}


</script>

<template>
  <form @submit.prevent="submit" @keydown.enter="() => {}">
    <div class="grid lg:grid-cols-2 md:grid-cols-2 grid-cols-1 gap-5">
      <div class="lg:col-span-2 md:col-span-2 col-span-1">
        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
          Enter the Lendee's Information
        </h4>
      </div>
      <div class="col-span-1">
        <ComboboxTextInput
          :field-model-value="emailAddress"
          :suggestions="filteredClientSuggestionsLegible"
          :selected-callback="selectClientFromSuggestions"
          label="Email" type="email" placeholder="Type your email"
          name="emailAddress"
          v-model="emailAddress"
          :error="emailAddressError"
          @input="fetchClientSuggestionsDebounced"
          @emptied="resetClientComboBoxes"
        />
      </div>

      <div class="col-span-1">
        <TextInput
          label="Confirm Email"
          type="email"
          placeholder="Confirm your email"
          name="confirmEmailAddress"
          v-model="confirmEmailAddress"
          :error="confirmEmailAddressError"
        />
      </div>

      <div class="col-span-1">
        <ComboboxTextInput
          :field-model-value="firstName"
          :suggestions="filteredClientSuggestionsLegible"
          :selected-callback="selectClientFromSuggestions"
          label="First name"
          type="text"
          placeholder="First name"
          name="firstname"
          v-model="firstName"
          :error="firstNameError"
          @input="fetchClientSuggestionsDebounced"
          @emptied="resetClientComboBoxes"
        />
      </div>

      <div class="col-span-1">
        <ComboboxTextInput
          :field-model-value="lastName"
          :suggestions="filteredClientSuggestionsLegible"
          :selected-callback="selectClientFromSuggestions"
          label="Last name"
          type="text"
          placeholder="Last name"
          name="lastname"
          v-model="lastName"
          :error="lastNameError"
          @input="fetchClientSuggestionsDebounced"
          @emptied="resetClientComboBoxes"
        />
      </div>
      <FormStepNavigation
        :processing-submit="processingSubmit"
        :submit="submit"
        :goBack="goBack"/>
    </div>
  </form>
</template>

<style scoped lang="scss">

</style>
