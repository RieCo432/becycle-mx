<script>
import clientView from '@/views/client/clientView.vue';
import requests from '@/requests';
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
    };
  },
  methods: {
    cancelAppointment(appointmentId) {
      console.log('cancel');
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
    ></client-view>
  </div>
</template>

<style scoped lang="scss">

</style>
