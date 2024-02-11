<script>
import FullCalendar from '@fullcalendar/vue3';
import Card from '@/components/Card';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import listPlugin from '@fullcalendar/list';
import AppointmentInfoModal from '@/components/Modal/AppointmentInfoModal.vue';

export default {
  name: 'appointmentCalendar',
  components: {
    AppointmentInfoModal,
    FullCalendar,
    Card,
  },
  props: {
    getAppointments: {
      type: Function,
      required: true,
    },
    openingDays: {
      type: Array,
      required: true,
    },
    openTime: {
      type: String,
      required: true,
    },
    closeTime: {
      type: String,
      required: true,
    },
    slotDuration: {
      type: String,
      required: true,
    },
  },
  methods: {
    showEventDetail(eventClickInfo) {
      console.log(eventClickInfo.event);
      this.showAppointmentModal = !this.showAppointmentModal;
      this.appointmentModalInfo = {
        title: eventClickInfo.event.title,
        startDateTime: eventClickInfo.event.start,
        notes: eventClickInfo.event.extendedProps.notes,
        id: eventClickInfo.event.id,
        client: eventClickInfo.event.extendedProps.client,
        endDateTime: eventClickInfo.event.end,
        confirmed: eventClickInfo.event.extendedProps.confirmed,
        cancelled: eventClickInfo.event.extendedProps.cancelled,
        clientName: eventClickInfo.event.extendedProps.clientName,
        typeTitle: eventClickInfo.event.extendedProps.typeTitle,
      };
    },
    refreshAppointments() {
      const calendarApi = this.$refs.fullCalendar.getApi();
      calendarApi.getEventSourceById('main').refetch();
    },
  },
  data() {
    return {
      calendarOptions: {
        headerToolbar: {
          left: 'prev,next today',
          center: 'title',
          right: 'timeGridWeek,timeGridDay,listWeek',
        },
        plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
        initialView: 'timeGridWeek',
        themeSystem: 'bootstrap',
        eventSources: [
          {
            id: 'main',
            events: async (fetchInfo) => await this.getAppointments(fetchInfo),
          },
        ],
        eventClick: this.showEventDetail,
        firstDay: 1,
        editable: true,
        droppable: true,
        selectable: true,
        selectMirror: true,
        dayMaxEvents: true,
        hiddenDays: Array.from({length: 7}, (x, i) => (i + 1)).filter((i) => !this.openingDays.includes(i - 1)).map((i) => (i % 7)),
        slotDuration: this.slotDuration,
        slotMinTime: this.openTime,
        slotMaxTime: this.closeTime,
        height: 'auto',
        nowIndicator: true,
        eventMaxStack: 6,
        slotEventOverlap: false,
      },
      showAppointmentModal: false,
      appointmentModalInfo: {},
    };
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      Test
      <Card>
        <div class="dashcode-calender">
          <FullCalendar
              ref="fullCalendar"
              :options="calendarOptions"
          ></FullCalendar>
        </div>
      </Card>
    </div>
    <AppointmentInfoModal
        :active-modal="showAppointmentModal"
        @close="showAppointmentModal = !showAppointmentModal"
        :appointment="appointmentModalInfo"
        @appointments-updated="refreshAppointments()"
    >
    </AppointmentInfoModal>
  </div>
</template>

<style lang="scss">
.fc-toolbar-chunk button {
  height: 50px;
  //min-width: 70px;
  &.fc-prev-button {
    &:after {
      // content: url("https://api.iconify.design/akar-icons/chevron-left.svg?color=white&width=24");
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
    }
  }
  &.fc-next-button {
    &:after {
      //content: url("https://api.iconify.design/akar-icons/chevron-right.svg?color=white&width=24");
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
    }
  }
}
.fc-button {
  font-size: 14px !important;
  line-height: 14px !important;
  height: auto !important;
  text-transform: capitalize !important;
  font-family: Inter !important;
  padding: 12px 20px 12px 20px !important;
}
.fc .fc-button-primary {
  color: #000 !important;
  &:hover {
    color: #fff !important;
  }
}
.fc .fc-button-primary.fc-button-active {
  color: #fff !important;
}
.dark {
  .fc .fc-button-primary {
    color: #fff !important;
  }
}
.fc .fc-button-primary {
  background: transparent !important;
  @apply dark:text-white border-slate-100 dark:border-slate-700;
}
.fc .fc-button-primary:not(:disabled):active,
.fc .fc-button-primary:not(:disabled).fc-button-active,
.fc .fc-button-primary:hover {
  background: #111112 !important;
}
.dark {
  .fc .fc-button-primary:not(:disabled):active,
  .fc .fc-button-primary:not(:disabled).fc-button-active,
  .fc .fc-button-primary:hover {
    background: #0f172a !important;
  }
}
.fc .fc-button-primary:disabled {
  background: #a0aec0 !important;
  border-color: #a0aec0 !important;
  @apply cursor-not-allowed;
}
.dark {
  .fc .fc-button-primary:disabled {
    background: #334155 !important;
    border-color: #334155 !important;
  }
}
.fc .fc-daygrid-day.fc-day-today {
  background: rgba(95, 99, 242, 0.04) !important;
}
.dark {
  .fc .fc-daygrid-day.fc-day-today {
    background: #334155 !important;
  }
}
.fc .fc-button-primary:focus {
  box-shadow: none !important;
}
.fc-theme-standard .fc-scrollgrid {
  border-color: #eef1f9 !important;
}
.dark {
  .fc-theme-standard .fc-scrollgrid {
    border-color: #334155 !important;
  }
}
.fc-theme-standard td,
.fc-theme-standard th {
  @apply border-slate-100 dark:border-slate-700;
}
.fc-col-header-cell .fc-scrollgrid-sync-inner {
  @apply bg-slate-50 dark:bg-slate-700  text-xs text-slate-500 dark:text-slate-300 font-normal py-3;
}
.fc-daygrid-day-top {
  @apply text-sm px-3 py-2  text-slate-900 dark:text-white font-normal;
}
.fc-h-event .fc-event-main-frame {
  @apply justify-center text-center w-max mx-auto;
  .fc-event-time {
    @apply font-normal flex-none;
  }
}
.fc-event-time {
  @apply text-sm font-normal;
}
.fc-event-title {
  font-size: 14px !important;
  font-weight: 300 !important;
}
.fc .fc-toolbar-title {
  @apply text-lg font-normal text-slate-600 dark:text-slate-300;
}
// event css
.fc-daygrid-event-dot {
  @apply hidden;
}
.dashcode-calender {
  .bg-primary-500 {
    @apply bg-[#4669FA] border-none text-white text-center px-2 font-medium text-sm;
  }
  .bg-secondary-500 {
    @apply bg-[#A0AEC0] border-none text-white text-center px-2 font-medium text-sm;
  }
  .bg-danger-500 {
    @apply bg-[#F1595C] border-none text-white text-center px-2 font-medium text-sm;
  }
  .bg-info {
    @apply bg-[#0CE7FA] border-none text-white text-center px-2 font-medium text-sm;
  }
  .bg-warning-500 {
    @apply bg-[#FA916B] border-none text-white text-center px-2 font-medium text-sm;
  }
  .bg-success-500 {
    @apply bg-[#50C793] border-none text-white text-center px-2 font-medium text-sm;
  }
  .bg-slate-800 {
    @apply bg-[#222] border-none text-white text-center px-2 font-medium text-sm;
  }
}
@media (max-width: 981px) {
  .fc-button-group,
  .fc .fc-toolbar {
    display: block !important;
  }
  .fc .fc-toolbar {
    @apply space-y-4;
  }
  .fc-toolbar-chunk {
    @apply space-y-4;
  }
  .fc .fc-button {
    padding: 0.4em 0.65em !important;
  }
}
.fc .fc-timegrid-axis-cushion,
.fc .fc-timegrid-slot-label-cushion {
  @apply dark:text-slate-300;
}
.fc .fc-list-event:hover td {
  @apply bg-inherit;
}
.fc .fc-list-event-dot {
  @apply hidden;
}
.fc-direction-ltr .fc-list-day-text,
.fc-direction-rtl .fc-list-day-side-text,
.fc-direction-ltr .fc-list-day-side-text,
.fc-direction-rtl .fc-list-day-text {
  font-size: 16px;
  font-weight: 500;
}
</style>
