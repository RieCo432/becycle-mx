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
    this.openTime = moment(new Date().setHours(...openingHours['open_time'].split(':')))
      .subtract(this.slotDurationMinutes, 'minutes').format('HH:mm:ss');
    this.closeTime = moment(new Date().setHours(...openingHours['close_time'].split(':')))
      .add(this.slotDurationMinutes, 'minutes').format('HH:mm:ss');
    this.loading = false;
  },
};
</script>

<template>
  <div>
    <AppointmentCalendar v-if="!loading"
                         :open-time="openTime"
                         :close-time="closeTime"
                         :opening-days="openingDays"
                         :slot-duration="slotDurationString"
    ></AppointmentCalendar>
  </div>
</template>

<style scoped lang="scss">

</style>
