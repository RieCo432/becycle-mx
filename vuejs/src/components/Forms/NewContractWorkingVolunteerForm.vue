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
  userSortingFunction: {
    type: Function,
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

const userSelectionOptionsStatic = ref(true);
const activeUsers = ref([]);

const filteredWorkingUserSuggestions = computed(() => activeUsers.value
  .filter((suggestion) => (
    suggestion
      .toLowerCase()
      .startsWith(workingUser.value.toLowerCase())
  ))
  .sort(props.userSortingFunction)
  .slice(0, 10));

requests.getActiveUsers().then((response) => {
  activeUsers.value = response.data.map((user) => (user.username));
  userSelectionOptionsStatic.value = true;
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 5000});
});


const workingUserSchema = yup.object().shape({
  workingUser: yup.string().required(' Main mechanic Username is required '),
  workingPasswordOrPin: yup.string().required(' Password or Pin is required '),
});

const {handleSubmit} = useForm({
  validationSchema: workingUserSchema,
  keepValuesOnUnmount: true,
});

const {value: workingUser, errorMessage: workingUserError} = useField('workingUser');
const {value: workingPasswordOrPin, errorMessage: workingPasswordOrPinError,
  setErrors: workingPasswordOrPinSetErrors} = useField('workingPasswordOrPin');

workingUser.value = '';

const submit = handleSubmit(() => {
  if (checkCurrentlyProcessing()) return;
  processingSubmit.value = true;

  requests.putDraftContractWorkingUser(props.draft.id, workingUser.value, workingPasswordOrPin.value)
    .then((response) => {
      toast.success('Working Volunteer Updated!', {timeout: 1000});
      emit('update:draft', response.data);
    })
    .catch((error) => {
      if (error.response.status === 400) {
        workingPasswordOrPinSetErrors('Wrong Password!');
      } else {
        toast.error(error.response.data.detail.description, {timeout: 5000});
      }
    })
    .finally(() => {
      processingSubmit.value = false;
    });
});

function goBack() {
  if (checkCurrentlyProcessing()) return;
  emit('goBack');
}

function selectWorkingUser(event, i) {
  if (i !== -1) {
    workingUser.value = filteredWorkingUserSuggestions.value[i];
    userSelectionOptionsStatic.value = false;
    workingPasswordOrPin.value = null;
  }
}


</script>

<template>
  <form @submit.prevent="submit" @keydown.enter="() => {}">
    <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
      <div class="col-span-full">
        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
          Main Mechanic
        </h4>
      </div>
      <div class="col-span-1">
        <ComboboxTextInput
          :field-model-value="workingUser"
          :suggestions="filteredWorkingUserSuggestions"
          :selected-callback="selectWorkingUser"
          :allow-new="false"
          :open-by-default="userSelectionOptionsStatic"
          label="Working Volunteer"
          type="text"
          placeholder="workshop"
          name="workingUser"
          v-model="workingUser"
          :error="workingUserError"
          @change="() => {}"
        />
      </div>
      <div class="col-span-1">
        <TextInput
          label="Working User Password or Pin"
          type="password"
          placeholder="Password or Pin"
          name="workingUserPasswordOrPin"
          v-model="workingPasswordOrPin"
          :error="workingPasswordOrPinError"
          hasicon/>
      </div>
      <div class="col-span-full">
        <FormStepNavigation
          :processing-submit="processingSubmit"
          :submit="submit"
          :goBack="goBack"/>
      </div>
    </div>
  </form>
</template>

<style scoped lang="scss">

</style>
