<script>
import Card from '@/components/Card/index.vue';
import ContractSummaryTable from '@/components/Tables/ContractSummaryTable.vue';
import AppointmentSummaryTable from '@/components/Tables/AppointmentSummaryTable.vue';
import {useCredentialsStore} from '@/store/credentialsStore';
import requests from '@/requests';
import DashButton from '@/components/Button/index.vue';
import ContractClientCardSkeleton from '@/components/Skeleton/ContractClientCardSkeleton.vue';
import Modal from '@/components/Modal/Modal.vue';

const credentialsStore = useCredentialsStore();

export default {
  name: 'clientView',
  components: {
    ContractClientCardSkeleton,
    DashButton,
    AppointmentSummaryTable,
    Card,
    Advanced: ContractSummaryTable,
    Modal,
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
    loadingClientDetails: {
      type: Boolean,
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
    openEditDetailsModal: {
      type: Function,
      required: true,
    },
  },

  data() {
    return {
      showCancelAppointmentModal: false,
      cancelAppointmentModalId: null,
      cancelAppointmentModalInfo: {},
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
          label: 'Returned Date',
          field: 'returnedDate',
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
          func: (appointmentId) => {
            this.cancelAppointmentModalId = appointmentId;
            this.cancelAppointmentModalInfo = this.appointmentSummaries.find((appointment) => appointment.id === appointmentId);
            this.showCancelAppointmentModal = true;
          },
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
  <div>
    <div class="grid grid-cols-12 gap-5">
      <div class="col-span-12">

        <Card title="Details">
          <ContractClientCardSkeleton v-if="loadingClientDetails"></ContractClientCardSkeleton>
          <template v-else>
            <div class="grid grid-cols-12 gap-5">
              <div class="col-span-full">
                <p class="text-base text-slate-700 dark:text-slate-300 capitalize">{{ client.firstName }} {{ client.lastName }}</p>
              </div>
              <div class="col-span-full">
                <p class="text-base text-slate-700 dark:text-slate-300">{{ client.emailAddress }}</p>
              </div>
              <div class="col-span-full">
                <DashButton @click="openEditDetailsModal">Edit Details</DashButton>
              </div>
            </div>
          </template>
        </Card>
      </div>
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
              <Modal
                  :active-modal="showCancelAppointmentModal"
                  title="Are you sure you want to cancel this appointment?"
                  @close="showCancelAppointmentModal = false">
                <p class="text-slate-700 dark:text-slate-300">
                    Date and Time: {{ new Date(Date.parse(cancelAppointmentModalInfo.startDateTime))
                    .toLocaleString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric',
                        hour: "2-digit", minute: "2-digit", hour12: false, }) }}
                </p>
                <p class="text-slate-700 dark:text-slate-300">Type: {{ cancelAppointmentModalInfo.type }}</p>
                <p class="text-slate-700 dark:text-slate-300">Notes: {{ cancelAppointmentModalInfo.notes }}</p>

                <template #footer>
                  <DashButton
                      class="btn-danger"
                      @click="() => {
                        cancelAppointment(cancelAppointmentModalId);
                        showCancelAppointmentModal = false;
                        cancelAppointmentModalId = null;
                      }"
                  >Cancel Appointment</DashButton>
                </template>

              </Modal>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>


</template>

<style scoped lang="scss">

</style>
