<script>
import clientView from '@/views/client/clientView.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Modal from '@/components/Modal/Modal.vue';
import Button from '@/components/Button/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {ref} from 'vue';

const toast = useToast();

export default {
  name: 'clientIndex',
  components: {
    Textinput, Button, Modal,
    clientView,
  },
  setup() {
    const client = ref({});
    const showEditDetailsModal = ref(false);

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
      requests.patchChangeDetails(client.value.id, {
        firstName: firstName.value,
        lastName: lastName.value,
        emailAddress: emailAddress.value,
      }).then((response) => {
        toast.success('Client Details updated', {timeout: 2000});
        client.value = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      }).finally(() => {
        showEditDetailsModal.value = false;
      });
    });

    return {
      client,
      showEditDetailsModal,
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
  data() {
    return {
      contracts: [],

      contractSummaries: [],
      appointments: [],
      appointmentSummaries: [],
      loadingClientDetails: true,
      loadingContracts: true,
      loadingAppointments: true,
    };
  },
  methods: {
    async updateAppointmentInSummaries(appointment) {
      const indexInArray = this.appointmentSummaries.findIndex((originalAppointment) => originalAppointment.id === appointment.id);
      const appointmentType = (await requests.getAppointmentType(appointment.typeId)).data;
      let status = 'past';
      if (appointment.cancelled) {
        status = 'cancelled';
      } else if (new Date(Date.parse(appointment.startDateTime)) > new Date()) {
        if (appointment['confirmed']) {
          status = 'confirmed';
        } else {
          status = 'pending';
        }
      }
      this.appointmentSummaries.splice(indexInArray, 1, {
        id: appointment.id,
        status: status,
        startDateTime: appointment.startDateTime,
        type: appointmentType['title'],
        duration: appointmentType['duration'],
        notes: appointment.notes,
      });
    },
    acceptAppointment(appointmentId) {
      requests.confirmAppointment(appointmentId).then((response) => {
        toast.success('Appointment confirmed!', {timeout: 2000});
        this.updateAppointmentInSummaries(response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    cancelAppointment(appointmentId) {
      requests.cancelAppointment(appointmentId).then((response) => {
        toast.warning('Appointment cancelled!', {timeout: 2000});
        this.updateAppointmentInSummaries(response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    editAppointmentNotes(appointmentId) {
      console.log('edit notes');
    },
    rescheduleAppointment(appointmentId) {
      console.log('reschedule');
    },
    viewContract(contractId) {
      this.$router.push(`/contracts/${contractId}`);
    },
    openEditDetailsModal() {
      this.firstName = this.client.firstName;
      this.lastName = this.client.lastName;
      this.emailAddress = this.client.emailAddress;
      this.confirmEmailAddress = this.client.emailAddress;

      this.showEditDetailsModal = true;
    },
  },
  async created() {
    requests.getClient(this.$route.params.clientId).then( async (response) => {
      this.client = response.data;
      this.loadingClientDetails = false;

      this.contracts = (await requests.getClientContracts(this.client.id, true, true, true)).data;
      this.appointments = (await requests.getClientAppointments(this.client.id, true, true)).data;

      this.contractSummaries = (await Promise.all(this.contracts.map(async (contract) => {
        const bike = (await requests.getBike(contract.bikeId)).data;
        let status = 'open';
        if (contract.returnedDate != null) {
          status = 'closed';
        } else {
          if (new Date(contract.endDate).getTime() < new Date().getTime()) {
            status = 'expired';
          }
        }
        return {
          id: contract.id,
          startDate: contract.startDate,
          endDate: contract.endDate,
          returnedDate: contract.returnedDate,
          bikeMake: bike['make'],
          bikeModel: bike.model,
          bikeColour: bike.colour,
          bikeDecals: bike.decals,
          bikeSerialNumber: bike.serialNumber,
          status: status,
        };
      })));
      this.loadingContracts = false;

      this.appointmentSummaries = (await Promise.all(this.appointments.map(async (appointment) => {
        const appointmentType = (await requests.getAppointmentType(appointment.typeId)).data;
        let status = 'past';
        if (appointment.cancelled) {
          status = 'cancelled';
        } else if (new Date(Date.parse(appointment.startDateTime)) > new Date()) {
          if (appointment['confirmed']) {
            status = 'confirmed';
          } else {
            status = 'pending';
          }
        }

        return {
          id: appointment.id,
          status: status,
          startDateTime: appointment.startDateTime,
          type: appointmentType['title'],
          duration: appointmentType['duration'],
          notes: appointment.notes,
        };
      })));
      this.loadingAppointments = false;
    });
  },
};
</script>

<template>
  <div>
    <client-view
        :client="client"
        :contract-summaries="contractSummaries"
        :appointment-summaries="appointmentSummaries"
        :cancel-appointment="cancelAppointment"
        :edit-appointment-notes="editAppointmentNotes"
        :reschedule-appointment="rescheduleAppointment"
        :view-contract="viewContract"
        :loading-contracts="loadingContracts"
        :loading-appointments="loadingAppointments"
        :accept-appointment="acceptAppointment"
        :is-client="false"
        :open-edit-details-modal="openEditDetailsModal"
        :loading-client-details="loadingClientDetails"
    ></client-view>
    <Modal :active-modal="showEditDetailsModal" @close="showEditDetailsModal = !showEditDetailsModal" title="Edit Details">
      <form @submit.prevent="submitChangeDetails">
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
          <div class="col-span-full">
            <Textinput
                label="Email Address"
                type="text"
                placeholder="email@exmaple.com"
                name="emailAddress"
                v-model="emailAddress"
                :error="emailAddressError"
            />
          </div>
          <div class="col-span-full">
            <Textinput
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
  </div>
</template>

<style scoped lang="scss">

</style>
