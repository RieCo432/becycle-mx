<script>
import Button from '@/components/Button/index.vue';
import Checkbox from '@/components/Switch/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import {useField, useForm} from 'vee-validate';
import * as yup from 'yup';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'CreateNewAppointmentTypeCard',
  components: {Card, Textinput, Checkbox, Button},
  emits: [
    'newAppointmentTypeCreated',
  ],
  setup(props, context) {
    const newAppointmentTypeSchema = yup.object().shape({
      newAppointmentTypeId: yup.string().max(5, 'No more than 5 characters').required('Appointment Type ID is required'),
      newAppointmentTypeTitle: yup.string().max(30, 'No more than 30 characters').required('Appointment Type Title is required'),
      newAppointmentTypeDescription: yup.string().max(300, 'No more than 300 characters').required('Appointment Type Description is required'),
      newAppointmentTypeDuration: yup.number('Must be a number').integer('Must be an integer').positive('Must be positive').required('Appointment Type Duration is required'),
      newAppointmentTypeActive: yup.bool(),
    });

    const {handleSubmit: handleNewAppointmentTypeSubmit, resetForm: resetNewAppointmentTypeForm} = useForm({
      validationSchema: newAppointmentTypeSchema,
      keepValuesOnUnmount: true,
    });

    const {value: newAppointmentTypeId, errorMessage: newAppointmentTypeIdError} = useField('newAppointmentTypeId');
    const {value: newAppointmentTypeTitle, errorMessage: newAppointmentTypeTitleError} = useField('newAppointmentTypeTitle');
    const {value: newAppointmentTypeDescription, errorMessage: newAppointmentTypeDescriptionError} = useField('newAppointmentTypeDescription');
    const {value: newAppointmentTypeDuration, errorMessage: newAppointmentTypeDurationError} = useField('newAppointmentTypeDuration');
    const {value: newAppointmentTypeActive} = useField('newAppointmentTypeActive');

    const postNewAppointmentTypeSubmit = handleNewAppointmentTypeSubmit(() => {
      requests.postNewAppointmentType({
        id: newAppointmentTypeId.value,
        title: newAppointmentTypeTitle.value,
        description: newAppointmentTypeDescription.value,
        duration: newAppointmentTypeDuration.value,
        active: newAppointmentTypeActive.value,
      }).then((response) => {
        context.emit('newAppointmentTypeCreated', response.data);
        resetNewAppointmentTypeForm();
        toast.success('New Appointment Type added', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      newAppointmentTypeId,
      newAppointmentTypeIdError,
      newAppointmentTypeTitle,
      newAppointmentTypeTitleError,
      newAppointmentTypeDescription,
      newAppointmentTypeDescriptionError,
      newAppointmentTypeDuration,
      newAppointmentTypeDurationError,
      newAppointmentTypeActive,
      postNewAppointmentTypeSubmit,
    }
  },
};
</script>

<template>
  <Card title="Appointment Types">
    <div class="grid grid-cols-12">
      <div class="col-span-12">
        <div>
          <form @submit.prevent="postNewAppointmentTypeSubmit" class="space-y-4">
            <Textinput
                label="New Appointment Type ID"
                type="text"
                placeholder="srep"
                name="newAppointmentTypeId"
                v-model="newAppointmentTypeId"
                :error="newAppointmentTypeIdError"
            />
            <Textinput
                label="New Appointment Type Title"
                type="text"
                placeholder="Small Repair"
                name="newAppointmentTypeTitle"
                v-model="newAppointmentTypeTitle"
                :error="newAppointmentTypeTitleError"
            />
            <Textinput
                label="New Appointment Type Description"
                type="text"
                placeholder="Fix something small, like tighten brakes"
                name="newAppointmentTypeDescription"
                v-model="newAppointmentTypeDescription"
                :error="newAppointmentTypeDescriptionError"
            />
            <Textinput
                label="New Appointment Type Duration"
                type="text"
                placeholder="15"
                name="newAppointmentTypeDuration"
                v-model="newAppointmentTypeDuration"
                :error="newAppointmentTypeDurationError"
            />
            <Checkbox
                label="Make Available?"
                name="newAppointmentTypeActive"
                v-model="newAppointmentTypeActive"
            />
            <Button type="submit" class="btn btn-dark block w-full text-center">
              Submit
            </Button>
          </form>
        </div>
      </div>
    </div>
  </Card>
</template>

<style scoped lang="scss">

</style>