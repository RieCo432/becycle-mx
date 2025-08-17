<script>
import Modal from '@/components/Modal/Modal.vue';
import Button from '@/components/Button/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import {toRef} from 'vue';

const toast = useToast();

export default {
  name: 'AppointmentCancellationModal',
  components: {TextInput, Button, Modal},
  setup(props, context) {
    const closeModal = toRef(props, 'closeModal');
    const cancellationSchema = yup.object().shape({
      reason: yup.string(),
    });

    const {handleSubmit} = useForm({
      validationSchema: cancellationSchema,
      keepValuesOnUnmount: true,
    });

    const {value: reason, errorMessage: reasonError} = useField('reason');

    const cancelAppointment = handleSubmit(() => {
      requests.cancelAppointment(props.appointment.id, {reason: reason.value}).then((response) => {
        toast.warning('Appointment Cancelled!', {timeout: 2000});
        context.emit('appointmentCancelled', response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      }).finally(() => {
        closeModal.value();
      });
    });
    return {
      reason,
      reasonError,
      cancelAppointment,
    };
  },
  emits: [
    'appointmentCancelled',
  ],
  props: {
    appointment: {
      type: Object,
      required: true,
    },
    showModal: {
      type: Boolean,
      required: true,
    },
    closeModal: {
      type: Function,
      required: false,
    },
  },
  mounted() {},
};
</script>

<template>
  <Modal :active-modal="showModal" @close="closeModal" title="Cancel Appointment">
    <form @submit.prevent="cancelAppointment">
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-12">
          <TextInput
              label="Reason"
              type="text"
              placeholder="Wrong type"
              name="reason"
              v-model="reason"
              :error="reasonError"
          />
        </div>
        <div class="col-span-12">
          <Button type="submit" class="btn bg-danger-500 dark:bg-danger-500 block w-full text-center">
            Cancel
          </Button>
        </div>
      </div>
    </form>
  </Modal>
</template>

<style scoped lang="scss">

</style>
