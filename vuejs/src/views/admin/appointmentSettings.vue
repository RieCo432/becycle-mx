<script>
import EditAppointmentGeneralSettingsCard from '@/components/Card/EditAppointmentGeneralSettingsCard.vue';
import EditAppointmentConcurrencySettingsCard from '@/components/Card/EditAppointmentConcurrencySettingsCard.vue';
import requests from '@/requests';
import AppointmentConcurrencySlider from '@/components/Slider/AppointmentConcurrencySlider.vue';
export default {
  name: 'appointmentSettings',
  components: {
    AppointmentConcurrencySlider,
    EditAppointmentGeneralSettingsCard,
    EditAppointmentConcurrencySettingsCard,
  },
  data() {
    return {
      loadingConcurrencyLimits: true,
      concurrencyLimits: [],
      weekDayOptionsShort: [],
      weekDaysColloquialShort: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      weekDaysColloquial: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
      weekDaysOptions: [],
    };
  },
  methods: {
    sortConcurrencyLimits(a, b) {
      const aD = a.weekDay;
      const bD = b.weekDay;
      const [aH, aM] = a.afterTime.split(':');
      const [bH, bM] = b.afterTime.split(':');

      return (aM - bM) + 60 * ((aH - bH) + 24 * (aD - bD));
    },
    addConcurrencyLimit(newConcurrencyLimit) {
      this.concurrencyLimits.push(newConcurrencyLimit);
      this.concurrencyLimits.sort(this.sortConcurrencyLimits);
    },
    removeConcurrencyLimit(weekDay, afterTime) {
      const indexInArray = this.concurrencyLimits.findIndex(
        (concurrencyLimit) => (concurrencyLimit.weekDay === weekDay && concurrencyLimit.afterTime === afterTime),
      );
      this.concurrencyLimits.splice(indexInArray, 1);
      this.concurrencyLimits.sort(this.sortConcurrencyLimits);
    },
    handleConcurrencyLimitAdjusted(originalWeekDay, originalAfterTime, updatedConcurrencyLimit) {
      const indexInArray = this.concurrencyLimits.findIndex(
        (concurrencyLimit) => (concurrencyLimit.weekDay === originalWeekDay && concurrencyLimit.afterTime === originalAfterTime),
      );
      this.concurrencyLimits.splice(indexInArray, 1, updatedConcurrencyLimit);
      this.concurrencyLimits.sort(this.sortConcurrencyLimits);
    },
    updateOpeningDays() {
      this.loadOpeningDaysAndConcurrencyLimits();
    },
    loadOpeningDaysAndConcurrencyLimits() {
      this.loadingConcurrencyLimits = true;
      Promise.all([
        requests.getAppointmentConcurrencyLimits(),
        requests.getOpeningDays()])
        .then(([concurrencyLimitsResponse, openingDaysResponse]) => {
          this.concurrencyLimits = concurrencyLimitsResponse.data;
          this.weekDayOptionsShort = openingDaysResponse.data.map((openingDay) => (
            {
              value: openingDay,
              label: this.weekDaysColloquialShort[openingDay],
            }
          ));
          this.loadingConcurrencyLimits = false;
        });
    },
  },
  created() {
    this.loadOpeningDaysAndConcurrencyLimits();
    for (let i = 0; i < this.weekDaysColloquial.length; i++) {
      this.weekDaysOptions.push(
        {
          value: i,
          label: this.weekDaysColloquial[i],
        },
      );
    }
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12 xl:col-span-4 2xl:col-span-6">
      <EditAppointmentGeneralSettingsCard
          :opening-days-options="weekDaysOptions"
          @opening-days-updated="updateOpeningDays"
      />
    </div>
    <div class="col-span-12 xl:col-span-8 2xl:col-span-6"
         v-for="weekDay in weekDayOptionsShort"
         :key="weekDay.value"
    >
      <EditAppointmentConcurrencySettingsCard
          :week-day-name="weekDaysColloquial[weekDay.value]"
          :week-day="weekDay.value"
          :week-day-options="weekDayOptionsShort"
          :concurrency-limits="concurrencyLimits.filter((cl) => cl.weekDay === weekDay.value)"
          @concurrency-limit-adjusted="handleConcurrencyLimitAdjusted"
          @concurrency-limit-deleted="removeConcurrencyLimit"
          @concurrency-limit-added="addConcurrencyLimit"/>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
