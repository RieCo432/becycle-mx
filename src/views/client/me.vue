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
    ></client-view>
  </div>
</template>

<script>

import requests from '@/requests';
import clientView from '@/views/client/clientView.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'ClientMe',
  components: {
    clientView,
  },
  data() {
    return {
      client: {},
      contracts: [],
      contractSummaries: [],
      appointments: [],
      appointmentSummaries: [],
      loadingContracts: true,
      loadingAppointments: true,
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
  },
  async created() {
    this.client = (await requests.getClientMe()).data;
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
