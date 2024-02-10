<script>
import AppointmentCalendar from '@/views/appointments/appointmentCalendar.vue';
import requests from '@/requests';
import moment from 'moment';

export default {
  name: 'appointmentsIndex',
  components: {
    AppointmentCalendar,
  },
  data() {
    return {
      appointments: [],
      appointmentSummaries: [],
      openTime: '16:00:00',
      closeTime: '20:00:00',
      openingDays: [0, 1, 2, 3, 4, 5, 6],
      slotDurationMinutes: 15,
      slotDurationString: '00:15:00',
      loading: true,
    };
  },
  async created() {
    this.openingDays = (await requests.getOpeningDays()).data;
    this.slotDurationMinutes = (await requests.getSlotDuration()).data;
    const hours = (Math.trunc(this.slotDurationMinutes / 60)).toString().padStart(2, '0');
    const minutes = (this.slotDurationMinutes - hours * 60).toString().padStart(2, '0');
    this.slotDurationString = `${hours}:${minutes}:00`;
    const openingHours = (await requests.getOpeningHours()).data;
    this.openTime = moment(new Date().setHours(...openingHours['open_time'].split(':'))).subtract(this.slotDuration, 'minutes').format('HH:mm:ss');
    this.closeTime = moment(new Date().setHours(...openingHours['close_time'].split(':'))).add(this.slotDuration, 'minutes').format('HH:mm:ss');
    this.appointments = (await requests.getAppointments(true, true)).data;
    this.appointmentSummaries = (await Promise.all(this.appointments.map(async (appointment, i) => {
      const client = (await requests.getClient(appointment['clientId'])).data;
      const clientName = `${client['firstName']} ${client['lastName']}`;
      const appointmentType = (await requests.getAppointmentType(appointment['typeId'])).data;
      const appointmentTypeTitle = appointmentType['title'];
      return {
        id: i,
        title: `${clientName} for ${appointmentTypeTitle}`,
        start: appointment['startDateTime'],
        end: appointment['endDateTime'],
        class: 'bg-success-500 text-white',
      };
    })));
    this.loading = false;
  },
};
</script>

<template>
  <div>
    <AppointmentCalendar v-if="!loading"
                         :appointments="appointmentSummaries"
                         :open-time="openTime"
                         :close-time="closeTime"
                         :opening-days="openingDays"
                         :slot-duration="slotDurationString"
    ></AppointmentCalendar>
  </div>
</template>

<style scoped lang="scss">

</style>
