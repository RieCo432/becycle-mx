<script>
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Button from '@/components/Button/index.vue';
import window from '@/mixins/window';
import Select from '@/components/Select/index.vue';

const toast = useToast();
export default {
  name: 'AppointmentConcurrencySlider',
  mixins: [window],
  components: {
    Select,
    Button,
    VueSlider,
  },
  data() {
    return {
      maxConcurrent: 0,
      afterTime: null,
      weekDay: null,
    };
  },
  emits: [
    'concurrencyLimitAdjusted',
    'concurrencyLimitDeleted',
  ],
  methods: {
    setNewLimit() {
      requests.patchAppointmentConcurrencyLimit(
        this.concurrencyLimit.weekDay,
        this.concurrencyLimit.afterTime,
        {maxConcurrent: this.maxConcurrent})
        .then((response) => {
          toast.success('Limit adjusted!', {timeout: 1000});
          this.$emit('concurrencyLimitAdjusted', response.data);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          this.loadConcurrencyLimit();
        });
    },
    setNewAfterTime(newAfterTime, newTimeAfterString, instance) {
      if (newTimeAfterString !== this.concurrencyLimit.afterTime) {
        requests.patchAppointmentConcurrencyLimit(
          this.concurrencyLimit.weekDay,
          this.concurrencyLimit.afterTime,
          {afterTime: newTimeAfterString})
          .then((response) => {
            toast.success('After Time adjusted!', {timeout: 1000});
            this.$emit('concurrencyLimitAdjusted', response.data);
          }).catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 2000});
            this.loadConcurrencyLimit();
          });
      }
    },
    setNewWeekDay() {
      requests.patchAppointmentConcurrencyLimit(
        this.concurrencyLimit.weekDay,
        this.concurrencyLimit.afterTime,
        {weekDay: parseInt(this.weekDay)})
        .then((response) => {
          toast.success('Limit adjusted!', {timeout: 1000});
          this.$emit('concurrencyLimitAdjusted', response.data);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          this.loadConcurrencyLimit();
        });
    },
    loadConcurrencyLimit() {
      this.maxConcurrent = this.concurrencyLimit.maxConcurrent;
      this.afterTime = this.concurrencyLimit.afterTime;
      this.weekDay = this.concurrencyLimit.weekDay;
    },
    deleteConcurrencyLimit() {
      requests.deleteAppointmentConcurrencyLimit(
        this.concurrencyLimit.weekDay,
        this.concurrencyLimit.afterTime)
        .then((response) => {
          toast.success('Concurrency Limit removed', {timeout: 2000});
          this.$emit('concurrencyLimitDeleted');
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          this.loadConcurrencyLimit();
        });
    },
  },
  props: {
    concurrencyLimit: {
      type: Object,
      required: true,
    },
    weekDayOptions: {
      type: Array,
      required: true,
    },
  },
  mounted() {
    this.loadConcurrencyLimit();
  },
};
</script>

<template>
  <div  class="col-span-12 2xl:col-span-1">
    <div class="h-full grid grid-cols-12 2xl:grid-cols-1 gap-4">
      <div class="col-span-6 2xl:col-span-1 2xl:h-64 items-center my-auto">
        <vue-slider
            v-model="maxConcurrent"
            :direction="window.width > 1536 ? 'btt' : 'ltr'"
            :drag-on-click="true"
            :clickable="false"
            :height="window.width > 1536 ? '100%' : ''"
            :width="window.width > 1536 ? '' : '100%'"
            :max="10"
            :min="0"
            @drag-end="setNewLimit"
            class="m-auto 2xl:h-full"
        ></vue-slider>
      </div>
      <div class="col-span-4 2xl:col-span-1 2xl:h-8 content-center">
        <Select
            @change="setNewWeekDay"
            :options="weekDayOptions"
            v-model="weekDay"
            name="weekDay"
        />
      </div>
      <div class="col-span-4 2xl:col-span-1 2xl:h-8 content-center">
        <flat-pickr
            class="form-control m-auto"
            id="d3"
            placeholder="Time picker"
            v-model="afterTime"
            :config="{ enableTime: true, noCalendar: true, dateFormat: 'H:i', time_24hr: true,
                       onClose: setNewAfterTime, minuteIncrement: 15 }"
        />
      </div>
      <div class="col-span-2 2xl:col-span-1 2xl:h-8 content-center">
        <Button @click="deleteConcurrencyLimit" type="submit" class="btn btn-sm btn-dark block w-full text-center m-auto">
          Delete
        </Button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
