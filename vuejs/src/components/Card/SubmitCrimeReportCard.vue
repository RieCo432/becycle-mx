<script lang="ts">
import {defineComponent, toRef} from 'vue';
import Card from '@/components/Card/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import DashButton from '@/components/Button/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';
import requests from '@/requests';


const toast = useToast();

export default defineComponent({
  name: 'SubmitCrimeReportCard',
  components: {DashButton, TextInput, Card},
  setup(props, context) {
    const contractId = toRef(props, 'contractId');

    const reportStolenSchema = yup.object().shape({
      crimeNumber: yup.string().required('Police crime number is required!'),
    });


    const {handleSubmit, handleReset} = useForm({
      validationSchema: reportStolenSchema,
      keepValuesOnUnmount: true,
    });

    const {value: crimeNumber, errorMessage: crimeNumberError} = useField('crimeNumber');

    const submit = handleSubmit(() => {
      requests.postCrimeReport({contractId: contractId.value, crimeNumber: crimeNumber.value})
        .then((response) => {
          context.emit('crimeReportAdded', response.data);
          toast.success('Crime Report Submitted.', {timeout: 1000});
          handleReset();
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 1000});
        });
    });

    return {
      crimeNumber,
      crimeNumberError,
      submit,
    };
  },
  props: {
    contractId: {
      type: String,
      required: true,
    },
  },
  emits: ['crimeReportAdded'],
});
</script>

<template>
  <Card title="Report Stolen">
    <form @submit.prevent="submit">
      <div class="grid grid-cols-1 gap-5">
        <TextInput
            label="Crime Report Number"
            type="text"
            placeholder="PS-XXXXXXXX-XXXX"
            name="crimeNumber"
            v-model="crimeNumber"
            :error="crimeNumberError"
        />

        <DashButton
            text="Report Stolen"
        />
      </div>

    </form>
  </Card>
</template>

<style scoped lang="scss">

</style>
