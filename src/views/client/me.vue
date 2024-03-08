<template>
  <div>
    <client-view
        :client="client"
        :contract-summaries="contractSummaries"
        :appointment-summaries="appointmentSummaries"
        :cancel-appointment="cancelMyAppointment"
        :edit-appointment-notes="editMyAppointmentNotes"
        :reschedule-appointment="rescheduleMyAppointment"
        :view-contract="viewContract"
        :loading-contracts="loadingContracts"
        :loading-appointments="loadingAppointments"
        :is-client="true"
        :open-edit-details-modal="openEditDetailsModal"
        :loading-client-details="loadingClientDetails"
    ></client-view>
    <Modal :active-modal="showEditDetailsModal" @close="showEditDetailsModal = !showEditDetailsModal" title="Edit Details">
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
  </div>
</template>

<script>

import requests from '@/requests';
import clientView from '@/views/client/clientView.vue';
import {useToast} from 'vue-toastification';
import Modal from '@/components/Modal/Modal.vue';
import Button from '@/components/Button/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {ref} from 'vue';

const toast = useToast();

export default {
  name: 'ClientMe',
  components: {
    Textinput, Button, Modal,
    clientView,
  },
  setup() {
    const client = ref({});
    const showEditDetailsModal = ref(false);

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
        client.value = response.data;
        toast.success('Details Updated!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      }).finally(() => {
        showEditDetailsModal.value = false;
      });
    });

    return {
      showEditDetailsModal,
      client,
      firstName,
      firstNameError,
      lastName,
      lastNameError,
      submitChangeNames,
    };
  },
  data() {
    return {
      loadingClientDetails: true,
      contracts: [],
      contractSummaries: [],
      appointments: [],
      appointmentSummaries: [],
      loadingContracts: true,
      loadingAppointments: true
    };
  },
  methods: {
    cancelMyAppointment(appointmentId) {
      requests.cancelMyAppointment(appointmentId).then(async (response) => {
        const appointment = response.data;
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
        const indexInArray = this.appointmentSummaries.findIndex((appointment) => appointment.id === appointmentId);
        this.appointmentSummaries.splice(indexInArray, 1, {
          id: appointment.id,
          status: status,
          startDateTime: appointment.startDateTime,
          type: appointmentType['title'],
          duration: appointmentType['duration'],
          notes: appointment.notes,
        });
        toast.warning('Appointment cancelled', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    editMyAppointmentNotes(appointmentId) {
      console.log('edit notes');
    },
    rescheduleMyAppointment(appointmentId) {
      console.log('reschedule');
    },
    viewContract(contractId) {
      this.$router.push(`/clients/me/contracts/${contractId}`);
    },
    openEditDetailsModal() {
      this.firstName = this.client.firstName;
      this.lastName = this.client.lastName;
      this.showEditDetailsModal = true;
    },
  },
  async created() {
    this.client = (await requests.getClientMe()).data;
    this.loadingClientDetails = false;
    this.contracts = (await requests.getMyContracts(true, true, true)).data;
    this.appointments = (await requests.getMyAppointments(true, true)).data;


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
  },
};


</script>


<style scoped lang="scss">

</style>
