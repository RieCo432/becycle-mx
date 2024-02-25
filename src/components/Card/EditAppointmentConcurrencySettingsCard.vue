<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import AppointmentConcurrencySlider from '@/components/Slider/AppointmentConcurrencySlider.vue';
import {useToast} from 'vue-toastification';
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import Button from '@/components/Button/index.vue';

const toast = useToast();

export default {
  name: 'EditAppointmentConcurrencySettingsCard',
  components: {
    Button,
    AppointmentConcurrencySlider,
    Card,
    VueSlider,
  },
  data() {
    return {
      loadingConcurrencyLimits: true,
      concurrencyLimits: [],
      newAfterTime: null,
      newLimit: 0,
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
      this.concurrencyLimits.sort(this.sortConcurrencyLimits);
    },
    sortConcurrencyLimits(a, b) {
      const [aH, aM] = a.afterTime.split(':');
      const [bH, bM] = b.afterTime.split(':');

      return 60 * (aH - bH) + (aM - bM);
    },
    removeConcurrencyLimit(afterTime) {
      const indexInArray = this.concurrencyLimits.findIndex((concurrencyLimit) => concurrencyLimit.afterTime === afterTime);
      this.concurrencyLimits.splice(indexInArray, 1);
      this.concurrencyLimits.sort(this.sortConcurrencyLimits);
    },
    postNewConcurrencyLimit() {
      if (this.newAfterTime == null) {
        toast.error('You must choose a time!', {timeout: 2000});
      } else {
        requests.postNewAppointmentConcurrencyLimit({
          afterTime: this.newAfterTime.concat(':00'),
          maxConcurrent: this.newLimit,
        }).then((response) => {
          this.concurrencyLimits.push(response.data);
          this.concurrencyLimits.sort(this.sortConcurrencyLimits);
          toast.success('Appointment Concurrency Limit added', {timeout: 2000});
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        }).finally(() => {
          this.newLimit = 0;
          this.newAfterTime = null;
        });
      }
    },
  },
};
</script>

<template>
  <Card title="Appointment Concurrency Settings">
    <div v-if="!loadingConcurrencyLimits" class="grid grid-cols-12 gap-5 h-full">
        <AppointmentConcurrencySlider
            v-for="concurrencyLimit in concurrencyLimits"
            :concurrency-limit="concurrencyLimit"
            :key="concurrencyLimit.afterTime"
            @concurrency-limit-adjusted="(updatedConcurrencyLimit) => handleConcurrencyLimitAdjusted(concurrencyLimit.afterTime, updatedConcurrencyLimit)"
            @concurrency-limit-deleted="() => removeConcurrencyLimit(concurrencyLimit.afterTime)"
            class="h-full"
        ></AppointmentConcurrencySlider>
      <div class="col-span-1 h-full col-end-13">
        <form @submit.prevent="postNewConcurrencyLimit">
          <div class="h-full grid grid-cols-1 gap-y-4">
            <div class="col-span-1 h-64">
              <vue-slider
                  name="newLimit"
                  v-model="newLimit"
                  direction="btt"
                  :drag-on-click="true"
                  :clickable="false"
                  height="100%"
                  :max="10"
                  :min="0"
                  class="mx-auto h-full"
              ></vue-slider>
            </div>
            <div class="col-span-1 h-8">
              <flat-pickr
                  class="form-control"
                  name="newAfterTime"
                  id="d3"
                  placeholder="hh:mm"
                  v-model="newAfterTime"
                  :config="{ enableTime: true, noCalendar: true, dateFormat: 'H:i', time_24hr: true }"
              >
              </flat-pickr>
            </div>
            <div class="col-span-1 h-8">
              <Button type="submit" class="btn btn-sm btn-dark block w-full text-center">
                Add
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </Card>
</template>

<style scoped lang="scss">

</style>