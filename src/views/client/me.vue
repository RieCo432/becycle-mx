<template>
  <div>
    <client-view
        :client="client"
        :contract-summaries="contractSummaries"
        :appointment-summaries="appointmentSummaries"
        :cancel-appointment="cancelMyAppointment"
        :edit-appointment-notes="editMyAppointmentNotes"
        :reschedule-appointment="rescheduleMyAppointment"
    ></client-view>
  </div>
</template>

<script>

import requests from '@/requests';
import clientView from '@/views/client/clientView.vue';

export default {
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
    };
  },
  methods: {
    cancelMyAppointment(appointmentId) {
      console.log('cancel');
    },
    editMyAppointmentNotes(appointmentId) {
      console.log('edit notes');
    },
    rescheduleMyAppointment(appointmentId) {
      console.log('reschedule');
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


<style scoped lang="scss">

</style>
