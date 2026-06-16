<script setup>

import Radio from '@/components/Radio/index.vue';
import Textarea from '@/components/Textarea/index.vue';
import {useToast} from 'vue-toastification';
import {ref} from 'vue';
import {ErrorMessage, useField, useForm} from 'vee-validate';
import * as yup from 'yup';
import requests from '@/requests';
import FormStepNavigation from '@/components/Forms/FormStepNavigation.vue';

const toast = useToast();

const emit = defineEmits(['goBack', 'update:draft']);
const props = defineProps({
  draft: {
    type: Object,
    required: true,
  },
});

const contractTypes = ref([]);
requests.getContractTypes()
  .then((response) => {
    contractTypes.value = response.data.map((t) => (t.id));
  });

const bikeConditions = ref([]);
requests.getBikeConditions()
  .then((response) => {
    bikeConditions.value = response.data;
  });

const processingSubmit = ref(false);
function checkCurrentlyProcessing() {
  if (processingSubmit.value) {
    toast.warning('Please wait for the previous action to complete');
    return true;
  }
  return false;
}

const contractSchema = yup.object().shape({
  type: yup.string().required(' Type is required'),
  condition: yup.string().required(' Condition is required '),
  notes: yup.string().nullable(),
});

const {handleSubmit} = useForm({
  validationSchema: contractSchema,
  keepValuesOnUnmount: true,
});

const {value: type, errorMessage: typeError} = useField('type');
const {value: condition, errorMessage: conditionError} = useField('condition');
const {value: notes, errorMessage: notesError} = useField('notes');

const submit = handleSubmit(() => {
  if (checkCurrentlyProcessing()) return;
  processingSubmit.value = true;

  requests.putDraftContractDetails(props.draft.id, type.value, condition.value, notes.value)
    .then((response) => {
      toast.success('Contract Details Updated!', {timeout: 1000});
      emit('update:draft', response.data);
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 5000});
    })
    .finally(() => {
      processingSubmit.value = false;
    });
});

function goBack() {
  if (checkCurrentlyProcessing()) return;
  emit('goBack');
}

</script>

<template>
  <form @submit.prevent="submit" @keydown.enter="() => {}">
    <div class="grid lg:grid-cols-6 md:grid-cols-4 grid-cols-2 gap-5">
      <div class="lg:col-span-6 md:col-span-4 col-span-2">
        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
          Additional Contract Information
        </h4>
      </div>

      <div class="col-span-1">
        <h5 class="text-base text-slate-800 dark:text-slate-300 mb-6">Contract Type</h5>
        <Radio
          v-for="(contractType, i) in contractTypes"
          :key="i"
          :label="contractType"
          class="mb-5"
          name="contracttype"
          v-model="type"
          :value="contractType"
        />
        <ErrorMessage name="type" :error="typeError" class="text-danger-500"/>
      </div>

      <div class="col-span-1">
        <h5 class="text-base text-slate-800 dark:text-slate-300 mb-6">Bike Condition</h5>
        <Radio
          v-for="(bikeCondition, i) in bikeConditions"
          :key="i"
          :label="bikeCondition"
          class="mb-5"
          name="bikecondition"
          v-model="condition"
          :value="bikeCondition"
        />
        <ErrorMessage name="condition" :error="conditionError" class="text-danger-500"/>
      </div>

      <div class="md:col-span-4 col-span-2">
        <Textarea
          label="Notes"
          type="text"
          placeholder="anything noteworth"
          name="notes"
          v-model="notes"
          :error="notesError"
        />
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
