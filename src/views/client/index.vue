<script>
import clientView from '@/views/client/clientView.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'clientIndex',
  components: {
    clientView,
  },
  data() {
    return {
      contracts: [],
      client: {},
      contractSummaries: [],
      appointments: [],
      appointmentSummaries: [],
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
  },
  async created() {
    this.client = (await requests.getClient(this.$route.params.clientId)).data;
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
    ></client-view>
  </div>
</template>

<style scoped lang="scss">

</style>
