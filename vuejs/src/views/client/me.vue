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
        :open-edit-details-modal="() => showEditDetailsModal = true"
        :loading-client-details="loadingClientDetails"
    ></client-view>
    <EditMyDetailsModal v-if="!loadingClientDetails"
                        :client="client"
                        :show-modal="showEditDetailsModal"
                        :close-modal="() => showEditDetailsModal = false"
                        @client-details-updated="clientDetailsUpdated"
    >
    </EditMyDetailsModal>
  </div>
</template>

<script>

import requests from '@/requests';
import clientView from '@/views/client/clientView.vue';
import {useToast} from 'vue-toastification';
import EditMyDetailsModal from '@/components/Modal/EditMyDetailsModal.vue';

const toast = useToast();

export default {
  name: 'ClientMe',
  components: {
    EditMyDetailsModal,
    clientView,
  },
  data() {
    return {
      client: {},
      loadingClientDetails: true,
      contracts: [],
      contractSummaries: [],
      appointments: [],
      appointmentSummaries: [],
      loadingContracts: true,
      loadingAppointments: true,
      showEditDetailsModal: false,
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
      // TODO
    },
    rescheduleMyAppointment(appointmentId) {
      // TODO
    },
    viewContract(contractId) {
      this.$router.push(`/clients/me/contracts/${contractId}`);
    },
    clientDetailsUpdated(updatedClient) {
      this.client = updatedClient;
      this.showEditDetailsModal = false;
    },
  },
  async created() {
    this.client = (await requests.getClientMe()).data;
    this.loadingClientDetails = false;
    this.contracts = (await requests.getMyContracts(true, true, true)).data;
    this.appointments = (await requests.getMyAppointments(true, true)).data;


    this.contractSummaries = (await Promise.all(this.contracts.map(async (contract) => {
      const bike = (await requests.getClientBike(contract.bikeId)).data;
      let status = 'open';
      if (contract.returnedDate != null) {
        status = 'closed';
      } else if (contract.crimeReports.filter((report) => report.closedOn === null).length > 0) {
        status = 'stolen';
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
