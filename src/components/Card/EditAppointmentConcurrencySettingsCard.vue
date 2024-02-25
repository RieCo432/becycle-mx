<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import AppointmentConcurrencySlider from '@/components/Slider/AppointmentConcurrencySlider.vue';
export default {
  name: 'EditAppointmentConcurrencySettingsCard',
  components: {
    AppointmentConcurrencySlider,
    Card,
  },
  data() {
    return {
      loadingConcurrencyLimits: true,
      concurrencyLimits: [],
    };
  },
  created() {
    requests.getAppointmentConcurrencyLimits().then((response) => {
      this.concurrencyLimits = response.data;
      this.loadingConcurrencyLimits = false;
    });
  },
  methods: {
    handleConcurrencyLimitAdjusted(originalAfterTime, updatedConcurrencyLimit) {
      const indexInArray = this.concurrencyLimits.findIndex((concurrencyLimit) => concurrencyLimit.afterTime === originalAfterTime);
      this.concurrencyLimits.splice(indexInArray, 1, updatedConcurrencyLimit);
      this.concurrencyLimits.sort((a, b) => {
        const [aH, aM] = a.afterTime.split(':');
        const [bH, bM] = b.afterTime.split(':');

        return 60 * (aH - bH) + (aM - bM);
      });
    },
  },
};
</script>

<template>
  <Card title="Appointment Concurrency Settings">
    <div v-if="!loadingConcurrencyLimits" class="grid grid-cols-8 gap-5 h-full">
        <AppointmentConcurrencySlider
            v-for="concurrencyLimit in concurrencyLimits"
            :concurrency-limit="concurrencyLimit"
            :key="concurrencyLimit.afterTime"
            @concurrency-limit-adjusted="(updatedConcurrencyLimit) => handleConcurrencyLimitAdjusted(concurrencyLimit.afterTime, updatedConcurrencyLimit)"
            class="h-full"
        ></AppointmentConcurrencySlider>
    </div>
  </Card>
</template>

<style scoped lang="scss">

</style>