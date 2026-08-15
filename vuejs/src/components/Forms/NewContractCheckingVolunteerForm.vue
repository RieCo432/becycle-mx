<script setup>

import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import TextInput from '@/components/TextInput/index.vue';
import FormStepNavigation from '@/components/Forms/FormStepNavigation.vue';
import {useToast} from 'vue-toastification';
import {ref, computed} from 'vue';
import * as yup from 'yup';
import requests from '@/requests';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import Checkbox from '@/components/Checkbox/index.vue';

const toast = useToast();

const emit = defineEmits(['goBack', 'update:draft']);
const props = defineProps({
  contract: {
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

const rentalCheckers = ref([]);

const filteredCheckingUserSuggestions = computed(() => rentalCheckers.value
  .filter((suggestion) => (
    suggestion
      .toLowerCase()
      .startsWith(checkingUser.value.toLowerCase())
  ))
  .sort(props.userSortingFunction)
  .slice(0, 10));


requests.getRentalCheckers().then((response) => {
  rentalCheckers.value = response.data.map((user) => (user.username));
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 5000});
});

const checkingUserSchema = yup.object().shape({
  checkingUser: yup.string().required(' Checking Username is required ')
    .notOneOf([props.contract.workingUser?.username], 'Checking volunteer must be different from working volunteer'),
  checkingPasswordOrPin: yup.string().required(' Password or Pin is required '),
  mCheckFrontWheelHub: yup.boolean().oneOf([true],
    'Is there no play in the front wheel and is it tightened correctly?')
    .required('Is there no play in the front wheel and is it tightened correctly?'),
  mCheckFrontWheelTire: yup.boolean().oneOf([true],
    'Is the front tire in good condition and seated correctly?')
    .required('Is the front tire in good condition and seated correctly?'),
  mCheckRearWheelHub: yup.boolean().oneOf([true],
    'Is there no play in the rear wheel and is it tightened correctly?')
    .required('Is there no play in the rear wheel and is it tightened correctly?'),
  mCheckRearWheelTire: yup.boolean().oneOf([true],
    'Is the rear tire in good condition and seated correctly?')
    .required('Is the rear tire in good condition and seated correctly?'),
  mCheckBottomBracket: yup.boolean().oneOf([true],
    'Is there no play in the bottom bracket and does it spin easily and smoothly?')
    .required('Is there no play in the bottom bracket and does it spin easily and smoothly?'),
  mCheckFrontBrake: yup.boolean().oneOf([true],
    'Is the front brake working fully?')
    .required('Is the front brake working fully?'),
  mCheckRearBrake: yup.boolean().oneOf([true], 'Is the rear brake working fully?')
    .required('Is the rear brake working fully?'),
  mCheckSeatPost: yup.boolean().oneOf([true],
    'Is the seat post set to correct height and properly tightened?')
    .required('Is the seat post set to correct height and properly tightened?'),
  mCheckHeadset: yup.boolean().oneOf([true],
    'Is there no play in the headset, does it steer easily and smoothly, and does it resist twisting?')
    .required('Is there no play in the headset, does it steer easily and smoothly, and does it resist twisting?'),
});

const {handleSubmit} = useForm({
  validationSchema: checkingUserSchema,
  keepValuesOnUnmount: true,
});

const {value: checkingUser, errorMessage: checkingUserError} = useField('checkingUser');
const {value: checkingPasswordOrPin, errorMessage: checkingPasswordOrPinError,
  setErrors: checkingPasswordOrPinSetErrors} = useField('checkingPasswordOrPin');
const {value: mCheckFrontWheelHub, errorMessage: mCheckFrontWheelHubError} = useField('mCheckFrontWheelHub');
const {value: mCheckFrontWheelTire, errorMessage: mCheckFrontWheelTireError} = useField('mCheckFrontWheelTire');
const {value: mCheckRearWheelHub, errorMessage: mCheckRearWheelHubError} = useField('mCheckRearWheelHub');
const {value: mCheckRearWheelTire, errorMessage: mCheckRearWheelTireError} = useField('mCheckRearWheelTire');
const {value: mCheckBottomBracket, errorMessage: mCheckBottomBracketError} = useField('mCheckBottomBracket');
const {value: mCheckFrontBrake, errorMessage: mCheckFrontBrakeError} = useField('mCheckFrontBrake');
const {value: mCheckRearBrake, errorMessage: mCheckRearBrakeError} = useField('mCheckRearBrake');
const {value: mCheckSeatPost, errorMessage: mCheckSeatPostError} = useField('mCheckSeatPost');
const {value: mCheckHeadset, errorMessage: mCheckHeadsetError} = useField('mCheckHeadset');


checkingUser.value = '';

const submit = handleSubmit(() => {
  if (checkCurrentlyProcessing()) return;
  processingSubmit.value = true;

  requests.putDraftContractCheckingUser(props.contract.id, checkingUser.value, checkingPasswordOrPin.value)
    .then((response) => {
      toast.success('Checking Volunteer Updated!', {timeout: 1000});
      emit('update:draft', response.data);
    })
    .catch((error) => {
      if (error.response.status === 400) {
        checkingPasswordOrPinSetErrors('Wrong Password!');
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

function selectCheckingUser(event, i) {
  if (i !== -1) {
    checkingUser.value = filteredCheckingUserSuggestions.value[i];
    checkingPasswordOrPin.value = null;
  }
}


</script>

<template>
  <form
    @submit.prevent="() => {
      if (!props.contract.checkingUserId || (checkingUser && checkingUser !== '') ) {
        submit()
      } else {
        emit('update:draft', props.contract)
      }
    }"
    @keydown.enter="() => {}">
    <div class="grid md:grid-cols-2 grid-cols-1 gap-5">
      <div class="col-span-full">
        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
          Main Mechanic
        </h4>
      </div>
      <div
        v-if="props.contract.checkingUserId"
        class="col-span-full">
        <h5 class="text-danger-500 dark:text-danger-500">
          This step has already been signed by {{ props.contract.checkingUser.username }}. You can still overwrite it.
        </h5>
      </div>
      <div class="col-span-full grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="col-span-1">
          <Checkbox
            label="M Check: Front Wheel?"
            name="mCheckFrontWheelHub"
            activeClass="ring-primary-500 bg-primary-500"
            v-model="mCheckFrontWheelHub"
            :error="mCheckFrontWheelHubError"/>
          <ErrorMessage
            name="mCheckFrontWheelHub"
            :error="mCheckFrontWheelHubError"
            class="text-danger-500"/>
        </div>
        <div class="col-span-1">
          <Checkbox
            label="M Check: Front Tire?"
            name="mCheckFrontWheelTire"
            activeClass="ring-primary-500 bg-primary-500"
            v-model="mCheckFrontWheelTire"
            :error="mCheckFrontWheelTireError"/>
          <ErrorMessage
            name="mCheckFrontWheelTire"
            :error="mCheckFrontWheelTireError"
            class="text-danger-500"/>
        </div>
        <div class="col-span-1">
          <Checkbox
            label="M Check: Rear Wheel?"
            name="mCheckRearWheelHub"
            activeClass="ring-primary-500 bg-primary-500"
            v-model="mCheckRearWheelHub"
            :error="mCheckRearWheelHubError"/>
          <ErrorMessage
            name="mCheckRearWheelHub"
            :error="mCheckRearWheelHubError"
            class="text-danger-500"/>
        </div>
        <div class="col-span-1">
          <Checkbox
            label="M Check: Rear Tire?"
            name="mCheckRearWheelTire"
            activeClass="ring-primary-500 bg-primary-500"
            v-model="mCheckRearWheelTire"
            :error="mCheckRearWheelTireError"/>
          <ErrorMessage
            name="mCheckRearWheelTire"
            :error="mCheckRearWheelTireError"
            class="text-danger-500"/>
        </div>
        <div class="col-span-1">
          <Checkbox
            label="M Check: Bottom Bracket?"
            name="mCheckBottomBracket"
            activeClass="ring-primary-500 bg-primary-500"
            v-model="mCheckBottomBracket"
            :error="mCheckBottomBracketError"/>
          <ErrorMessage
            name="mCheckBottomBracket"
            :error="mCheckBottomBracketError"
            class="text-danger-500"/>
        </div>
        <div class="col-span-1">
          <Checkbox
            label="M Check: Front Brake?"
            name="mCheckFrontBrake"
            activeClass="ring-primary-500 bg-primary-500"
            v-model="mCheckFrontBrake"
            :error="mCheckFrontBrakeError"/>
          <ErrorMessage
            name="mCheckFrontBrake"
            :error="mCheckFrontBrakeError"
            class="text-danger-500"/>
        </div>
        <div class="col-span-1">
          <Checkbox
            label="M Check: Rear Brake?"
            name="mCheckRearBrake"
            activeClass="ring-primary-500 bg-primary-500"
            v-model="mCheckRearBrake"
            :error="mCheckRearBrakeError"/>
          <ErrorMessage
            name="mCheckRearBrake"
            :error="mCheckRearBrakeError"
            class="text-danger-500"/>
        </div>
        <div class="col-span-1">
          <Checkbox
            label="M Check: Seat Post?"
            name="mCheckSeatPost"
            activeClass="ring-primary-500 bg-primary-500"
            v-model="mCheckSeatPost"
            :error="mCheckSeatPostError"/>
          <ErrorMessage
            name="mCheckSeatPost"
            :error="mCheckSeatPostError"
            class="text-danger-500"/>
        </div>
        <div class="col-span-1">
          <Checkbox
            label="M Check: Headset?"
            name="mCheckHeadset"
            activeClass="ring-primary-500 bg-primary-500"
            v-model="mCheckHeadset"
            :error="mCheckHeadsetError"/>
          <ErrorMessage
            name="mCheckHeadset"
            :error="mCheckHeadsetError"
            class="text-danger-500"/>
        </div>
      </div>
      <div class="md:col-span-2 col-span-1">
        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
          Checking Volunteer
        </h4>
      </div>
      <div class="col-span-1">
        <ComboboxTextInput
          :field-model-value="checkingUser"
          :suggestions="filteredCheckingUserSuggestions"
          :selected-callback="selectCheckingUser"
          :allow-new="false"
          label="Safety Checking User"
          type="text"
          placeholder="workshop"
          name="checkingUser"
          v-model="checkingUser"
          :error="checkingUserError"
          @change="() => {}"
        />
      </div>
      <div class="col-span-1">
        <TextInput
          label="Checking User Password or Pin"
          type="password"
          placeholder="Password Or Pin"
          name="checkingPasswordOrPin"
          v-model="checkingPasswordOrPin"
          :error="checkingPasswordOrPinError"
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
