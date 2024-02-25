<script>
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import requests from '@/requests';
import {useToast} from 'vue-toastification';

const toast = useToast();
export default {
  name: 'AppointmentConcurrencySlider',
  components: {
    VueSlider,
  },
  data() {
    return {
      maxConcurrent: 0,
      afterTime: null,
    };
  },
  emits: [
      'concurrencyLimitAdjusted',
  ],
  methods: {
    setNewLimit(newLimit) {
      requests.patchAppointmentConcurrencyLimit(this.concurrencyLimit.afterTime, {maxConcurrent: this.maxConcurrent}).then((response) => {
        toast.success('Limit adjusted!', {timeout: 1000});
        this.$emit('concurrencyLimitAdjusted', response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
        this.loadConcurrencyLimit();
      });
    },
    setNewAfterTime(newAfterTime, newTimeAfterString, instance) {
      newTimeAfterString = newTimeAfterString.concat(':00');
      if (newTimeAfterString !== this.concurrencyLimit.afterTime) {
        requests.patchAppointmentConcurrencyLimit(this.concurrencyLimit.afterTime, {afterTime: newTimeAfterString}).then((response) => {
          toast.success('After Time adjusted!', {timeout: 1000});
          this.$emit('concurrencyLimitAdjusted', response.data);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          this.loadConcurrencyLimit();
        });
      }
    },
    loadConcurrencyLimit() {
      this.maxConcurrent = this.concurrencyLimit.maxConcurrent;
      this.afterTime = this.concurrencyLimit.afterTime;
    },
  },
  props: {
    concurrencyLimit: {
      type: Object,
      required: true,
    },
  },
  mounted() {
    this.loadConcurrencyLimit();
  },
};
</script>

<template>
  <div  class="col-span-1">
    <div class="h-full grid grid-cols-1 gap-y-4">
      <div class="col-span-1 h-72">
        <vue-slider
            v-model="maxConcurrent"
            direction="btt"
            :drag-on-click="true"
            :clickable="false"
            height="100%"
            :max="10"
            :min="0"
            @drag-end="(newLimit) => setNewLimit(newLimit)"
            class="mx-auto h-full"
        ></vue-slider>
      </div>
      <div class="col-span-1 h-8">
        <flat-pickr
            class="form-control"
            id="d3"
            placeholder="Time picker"
            v-model="afterTime"
            :config="{ enableTime: true, noCalendar: true, dateFormat: 'H:i', time_24hr: true, onClose: setNewAfterTime, minuteIncrement: 15 }"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>