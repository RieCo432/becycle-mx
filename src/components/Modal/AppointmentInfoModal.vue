<template>
  <TransitionRoot :show="activeModal" as="template">
    <Dialog as="div" class="relative z-[99999]">
      <TransitionChild
          :enter="noFade ? '' : 'duration-300 ease-out'"
          :enter-from="noFade ? '' : 'opacity-0'"
          :enter-to="noFade ? '' : 'opacity-100'"
          :leave="noFade ? '' : 'duration-200 ease-in'"
          :leave-from="noFade ? '' : 'opacity-100'"
          :leave-to="noFade ? '' : 'opacity-0'"
      >
        <div
            class="fixed inset-0 bg-slate-900/50 backdrop-filter backdrop-blur-sm"
            v-if="disableBackdrop === false"
        />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div
            class="flex min-h-full justify-center text-center p-6"
            :class="centered ? 'items-center' : 'items-start '"
        >
          <TransitionChild
              as="template"
              :enter="noFade ? '' : 'duration-300  ease-out'"
              :enter-from="noFade ? '' : 'opacity-0 scale-95'"
              :enter-to="noFade ? '' : 'opacity-100 scale-100'"
              :leave="noFade ? '' : 'duration-200 ease-in'"
              :leave-from="noFade ? '' : 'opacity-100 scale-100'"
              :leave-to="noFade ? '' : 'opacity-0 scale-95'"
          >
            <DialogPanel
                class="w-full transform overflow-hidden rounded-md bg-white dark:bg-slate-800 text-left align-middle shadow-xl transition-all"
                :class="sizeClass"
            >
              <div
                  class="relative overflow-hidden py-4 px-5 text-white flex justify-between"
                  :class="themeClass">
                <h2 class="capitalize leading-6 tracking-wider font-medium text-base text-white">
                  Appointment Info
                </h2>
                <button @click="close" class="text-[22px]">
                  <Icon icon="heroicons-outline:x" />
                </button>
              </div>
              <div
                  class="px-6 py-8 dark:text-white"
                  :class="scrollContent ? 'overflow-y-auto max-h-[400px]' : ''">
                <p v-if="appointment.typeTitle !== 'Closed Day'">Name: {{appointment.clientName}}</p>
                <p>Type: {{appointment.typeTitle}}</p>
                <p v-if="appointment.typeTitle !== 'Closed Day'">Time: {{appointment.startDateTime.getHours()}}:{{appointment.startDateTime.getMinutes()}} - {{appointment.endDateTime.getHours()}}:{{appointment.endDateTime.getMinutes()}}</p>
                <p v-if="appointment.typeTitle !== 'Closed Day'">Confirmed: {{appointment.confirmed ? 'Yes' : 'No'}}</p>
                <p>Notes: {{appointment.notes}}</p>
              </div>
              <div v-if="appointment.typeTitle !== 'Closed Day'" class="px-4 justify-end py-3 flex space-x-3 border-t border-slate-100 dark:border-slate-700">
                <DashButton
                    class="mr-auto"
                    @click="$router.push({path: `/clients/${appointment.client.id}`})"
                >View Client</DashButton>
                <DashButton
                    class="bg-success-500 dark:bg-success-500"
                    v-if="!appointment.confirmed && !appointment.cancelled"
                    @click="confirmAppointment"
                >Accept</DashButton>
                <DashButton
                    class="bg-danger-500 dark:bg-danger-500"
                    v-if="!appointment.cancelled"
                    @click="cancelAppointment"
                >{{ appointment.confirmed ? 'Cancel' : 'Deny'}} Appointment</DashButton>
              </div>
              <div v-else class="px-4 justify-end py-3 flex space-x-3 border-t border-slate-100 dark:border-slate-700">
                <DashButton
                    class="bg-danger-500 dark:bg-danger-500"
                    @click="deleteClosedDay()"
                >Remove Closed Day</DashButton>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script>
import Icon from '@/components/Icon';
import DashButton from '@/components/Button';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
} from '@headlessui/vue';

const toast = useToast();

export default {
  name: 'appointmentInfoModal',
  components: {
    Icon,
    TransitionRoot,
    TransitionChild,
    Dialog,
    DialogPanel,
    DashButton,
  },
  methods: {
    confirmAppointment() {
      requests.confirmAppointment(this.appointment.id).then(() => {
        toast.success('Appointment Confirmed', {timeout: 2000});
        this.$emit('appointmentsUpdated');
      });
      this.close();
    },
    cancelAppointment() {
      requests.cancelAppointment(this.appointment.id).then(() => {
        toast.warning('Appointment Denied/Cancelled', {timeout: 2000});
        this.$emit('appointmentsUpdated');
      });
      this.close();
    },
    deleteClosedDay() {
      requests.deleteClosedDay(`${this.appointment.startDateTime.getFullYear()}-${(this.appointment.startDateTime.getMonth() + 1).toString().padStart(2, '0')}-${this.appointment.startDateTime.getDate().toString().padStart(2, '0')}`).then(() => {
        toast.warning('Closed Day Removed', {timeout: 2000});
        this.$emit('appointmentsUpdated');
      });
      this.close();
    },
  },
  emits: ['appointmentsUpdated'],
  props: {
    centered: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      default: 'Basic Modal',
    },
    label: {
      type: String,
      default: 'Basic Modal',
    },
    disableBackdrop: {
      type: Boolean,
      default: false,
    },
    noFade: {
      type: Boolean,
      default: false,
    },
    themeClass: {
      type: String,
      default:
          'bg-slate-900 dark:bg-slate-800 dark:border-b dark:border-slate-700',
    },
    sizeClass: {
      type: String,
      default: 'max-w-xl',
    },
    scrollContent: {
      type: Boolean,
      default: false,
    },
    activeModal: {
      type: Boolean,
      default: false,
    },
    appointment: {
      type: Object,
      required: true,
    },
  },
  setup(props, {emit}) {
    const close = () => {
      emit('close');
    };
    return {
      close,
    };
  },
};
</script>
