<script>
import Modal from '@/components/Modal/Modal.vue';
import Button from '@/components/Button/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import {toRef} from 'vue';

const toast = useToast();

export default {
  name: 'EditMyDetailsModal',
  components: {Textinput, Button, Modal},
  setup(props, context) {
    const closeModal = toRef(props, 'closeModal');
    const nameChangeSchema = yup.object().shape({
      firstName: yup.string().required('First name is required'),
      lastName: yup.string().required('Last name is required'),
    });

    const {handleSubmit} = useForm({
      validationSchema: nameChangeSchema,
      keepValuesOnUnmount: true,
    });

    const {value: firstName, errorMessage: firstNameError} = useField('firstName');
    const {value: lastName, errorMessage: lastNameError} = useField('lastName');

    const submitChangeNames = handleSubmit(() => {
      requests.patchChangeNames({firstName: firstName.value, lastName: lastName.value}).then((response) => {
        toast.success('Details Updated!', {timeout: 2000});
        context.emit('clientDetailsUpdated', response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      }).finally(() => {
        closeModal.value();
      });
    });
    return {
      firstName,
      firstNameError,
      lastName,
      lastNameError,
      submitChangeNames,
    };
  },
  emits: [
    'clientDetailsUpdated',
  ],
  props: {
    client: {
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
  mounted() {
    this.firstName = this.client.firstName;
    this.lastName = this.client.lastName;
  },
};
</script>

<template>
  <Modal :active-modal="showModal" @close="closeModal" title="Edit Details">
    <form @submit.prevent="submitChangeNames">
      <div class="grid grid-cols-12 gap-5">
        <div class="md:col-span-6 col-span-12">
          <Textinput
              label="First Name"
              type="text"
              placeholder="First Name"
              name="firstName"
              v-model="firstName"
              :error="firstNameError"
          />
        </div>
        <div class="md:col-span-6 col-span-12">
          <Textinput
              label="Last Name"
              type="text"
              placeholder="Last Name"
              name="lastName"
              v-model="lastName"
              :error="lastNameError"
          />
        </div>
        <div class="col-span-12">
          <Button type="submit" class="btn btn-dark block w-full text-center">
            Submit
          </Button>
        </div>
      </div>
    </form>
  </Modal>
</template>

<style scoped lang="scss">

</style>
