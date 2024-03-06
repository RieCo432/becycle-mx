<script>
import Card from '@/components/Card/index.vue';
import ContractSummaryTable from '@/components/Tables/ContractSummaryTable.vue';
import AppointmentSummaryTable from '@/components/Tables/AppointmentSummaryTable.vue';
import {useCredentialsStore} from '@/store/credentialsStore';
import TableSkeleton from '@/components/Skeleton/TableSkeleton.vue';
import requests from '@/requests';

const credentialsStore = useCredentialsStore();

export default {
  name: 'clientView',
  components: {
    TableSkeleton,
    AppointmentSummaryTable,
    Card,
    Advanced: ContractSummaryTable,
  },
  props: {
    client: {
      required: true,
      type: Object,
    },
    contractSummaries: {
      required: true,
      type: Array,
    },
    appointmentSummaries: {
      required: true,
      type: Array,
    },
    cancelAppointment: {
      type: Function,
      required: true,
    },
    acceptAppointment: {
      type: Function,
      default: () => {},
    },
    editAppointmentNotes: {
      type: Function,
      required: true,
    },
    rescheduleAppointment: {
      type: Function,
      required: true,
    },
    viewContract: {
      type: Function,
      required: true,
    },
    loadingContracts: {
      type: Boolean,
      required: true,
    },
    loadingAppointments: {
      type: Boolean,
      required: true,
    },
    isClient: {
      type: Boolean,
      required: true,
    },
  },

  data() {
    return {
      userIsAppointmentManager: false,
      contractActions: [
        {
          name: 'View',
          icon: 'heroicons-outline:eye',
        }, ...(credentialsStore.isUserLoggedIn() ? [{
          name: 'Return',
          icon: 'heroicons:pencil-square',
        }] : []),
      ],
      contractColumns: [
        {
          label: 'Status',
          field: 'status',
        },
        {
          label: 'Start Date',
          field: 'startDate',
        },
        {
          label: 'End Date',
          field: 'endDate',
        },
        {
          label: 'Make',
          field: 'bikeMake',
        },
        {
          label: 'Model',
          field: 'bikeModel',
        },

        {
          label: 'Colour',
          field: 'bikeColour',
        },

        {
          label: 'Decals',
          field: 'bikeDecals',
        },

        {
          label: 'Serial Number',
          field: 'bikeSerialNumber',
        },
        {
          label: 'Action',
          field: 'action',
        },
      ],

      appointmentActions: [
        /*{
          label: 'Edit Notes',
          id: 'edit',
          icon: 'heroicons:pencil-square',
        },*/
        /*{
          label: 'Reschedule',
          id: 'reschedule',
          icon: 'heroicons:clock',
        },*/
          ...!this.isClient ? [{
          label: 'Confirm Appointment',
          id: 'confirm',
          icon: 'heroicons-outline:check',
          func: (appointmentId) => this.acceptAppointment(appointmentId),
        }] : [],
        {
          label: 'Cancel Appointment',
          id: 'cancel',
          icon: 'heroicons-outline:x-mark',
          func: (appointmentId) => this.cancelAppointment(appointmentId),
        },
      ],
      appointmentColumns: [
        {
          label: 'Status',
          field: 'status',
        },
        {
          label: 'Date and Time',
          field: 'startDateTime',
        },
        {
          label: 'Type',
          field: 'type',
        },
        {
          label: 'Duration (minutes)',
          field: 'duration',
        },
        {
          label: 'Notes',
          field: 'notes',
        },
        {
          label: 'Action',
          field: 'action',
        },
      ],


    };
  },
  created() {
    if (credentialsStore.getTokenType() === 'user') {
      requests.getUserMe().then((response) => {
        this.userIsAppointmentManager = response.data.appointmentManager;
      });
    }
  },
  computed: {
    name() {
      return this.client.firstName + ' ' + this.client.lastName;
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card>
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <Advanced
                :loading="loadingContracts"
                :actions="contractActions"
                :columns="contractColumns"
                :advanced-table="contractSummaries"
                title="Contracts"
                :view-contract="viewContract">
            </Advanced>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12">
      <Card>

        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <AppointmentSummaryTable
                :loading="loadingAppointments"
                :cancel-appointment="cancelAppointment"
                :edit-appointment-notes="editAppointmentNotes"
                :reschedule-appointment="rescheduleAppointment"
                :actions="appointmentActions"
                :columns="appointmentColumns"
                :advanced-table="appointmentSummaries"
                :user-is-appointment-manager="userIsAppointmentManager"
                :is-client="isClient"
                title="Appointments">
            </AppointmentSummaryTable>
          </div>
        </div>
      </Card>
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>
