<script>
import Modal from '@/components/Modal/Modal.vue';
import Button from '@/components/Button/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import {toRef} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'EditClientDetailsModal',
  components: {TextInput, Button, Modal},
  setup(props, context) {
    const closeModal = toRef(props, 'closeModal');
    const client = toRef(props, 'client');
    const newDetailsSchema = yup.object().shape({
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
      validationSchema: newDetailsSchema,
      keepValuesOnUnmount: true,
    });

    const {value: emailAddress, errorMessage: emailAddressError} = useField('emailAddress');
    const {value: confirmEmailAddress, errorMessage: confirmEmailAddressError} = useField('confirmEmailAddress');
    const {value: firstName, errorMessage: firstNameError} = useField('firstName');
    const {value: lastName, errorMessage: lastNameError} = useField('lastName');

    const submitChangeDetails = handleSubmit(() => {
      requests.patchClientChangeDetails(client.value.id, {
        firstName: firstName.value,
        lastName: lastName.value,
        emailAddress: emailAddress.value,
      }).then((response) => {
        toast.success('Client Details updated', {timeout: 2000});
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
      emailAddress,
      emailAddressError,
      confirmEmailAddress,
      confirmEmailAddressError,
      submitChangeDetails,
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
      required: true,
    },
  },
  mounted() {
    this.firstName = this.client.firstName;
    this.lastName = this.client.lastName;
    this.emailAddress = this.client.emailAddress;
    this.confirmEmailAddress = this.client.emailAddress;
  },
};
</script>

<template>
  <Modal :active-modal="showModal" @close="closeModal" title="Edit Details">
    <form @submit.prevent="submitChangeDetails">
      <div class="grid grid-cols-12 gap-5">
        <div class="md:col-span-6 col-span-12">
          <TextInput
              label="First Name"
              type="text"
              placeholder="First Name"
              name="firstName"
              v-model="firstName"
              :error="firstNameError"
          />
        </div>
        <div class="md:col-span-6 col-span-12">
          <TextInput
              label="Last Name"
              type="text"
              placeholder="Last Name"
              name="lastName"
              v-model="lastName"
              :error="lastNameError"
          />
        </div>
        <div class="col-span-full">
          <TextInput
              label="Email Address"
              type="text"
              placeholder="email@exmaple.com"
              name="emailAddress"
              v-model="emailAddress"
              :error="emailAddressError"
          />
        </div>
        <div class="col-span-full">
          <TextInput
              label="Confirm Email Address"
              type="text"
              placeholder="email@exmaple.com"
              name="confirmEmailAddress"
              v-model="confirmEmailAddress"
              :error="confirmEmailAddressError"
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
