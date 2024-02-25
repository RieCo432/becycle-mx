<script>
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Button from '@/components/Button/index.vue';

const toast = useToast();
export default {
  name: 'AppointmentConcurrencySlider',
  components: {
    Button,
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
      'concurrencyLimitDeleted',
  ],
  methods: {
    setNewLimit() {
      requests.patchAppointmentConcurrencyLimit(this.concurrencyLimit.afterTime, {maxConcurrent: this.maxConcurrent}).then((response) => {
        toast.success('Limit adjusted!', {timeout: 1000});
        this.$emit('concurrencyLimitAdjusted', response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
        this.loadConcurrencyLimit();
      });
    },
    setNewAfterTime(newAfterTime, newTimeAfterString, instance) {
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
    deleteConcurrencyLimit() {
      requests.deleteAppointmentConcurrencyLimit(this.afterTime).then((response) => {
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
  },
  mounted() {
    this.loadConcurrencyLimit();
  },
};
</script>

<template>
  <div  class="col-span-1">
    <div class="h-full grid grid-cols-1 gap-y-4">
      <div class="col-span-1 h-64">
        <vue-slider
            v-model="maxConcurrent"
            direction="btt"
            :drag-on-click="true"
            :clickable="false"
            height="100%"
            :max="10"
            :min="0"
            @drag-end="setNewLimit"
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
      <div class="col-span-1 h-8">
        <Button @click="deleteConcurrencyLimit" type="submit" class="btn btn-sm btn-dark block w-full text-center">
          Delete
        </Button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>