<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import AppointmentConcurrencySlider from '@/components/Slider/AppointmentConcurrencySlider.vue';
import {useToast} from 'vue-toastification';
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import Button from '@/components/Button/index.vue';
import ConcurrencyLimitsSkeleton from '@/components/Skeleton/ConcurrencyLimitsSkeleton.vue';
import window from '@/mixins/window';

const toast = useToast();

export default {
  name: 'EditAppointmentConcurrencySettingsCard',
  mixins: [window],
  components: {
    Button,
    AppointmentConcurrencySlider,
    Card,
    VueSlider,
    ConcurrencyLimitsSkeleton,
  },
  data() {
    return {
      loadingConcurrencyLimits: true,
      concurrencyLimits: [],
      newAfterTime: null,
      newLimit: 0,
      weekDayOptions: [],
      weekDaysColloquial: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    };
  },
  created() {
    Promise.all([
      requests.getAppointmentConcurrencyLimits(),
      requests.getOpeningDays()])
      .then(([concurrencyLimitsResponse, openingDaysResponse]) => {
        this.concurrencyLimits = concurrencyLimitsResponse.data;
        this.weekDayOptions = openingDaysResponse.data.map((openingDay) => (
          {
            value: openingDay,
            label: this.weekDaysColloquial[openingDay],
          }
        ));
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
            :week-day-options="weekDayOptions"
            @concurrency-limit-adjusted="(updatedConcurrencyLimit) =>
              handleConcurrencyLimitAdjusted(concurrencyLimit.afterTime, updatedConcurrencyLimit)"
            @concurrency-limit-deleted="() => removeConcurrencyLimit(concurrencyLimit.afterTime)"
            class="h-full"
        ></AppointmentConcurrencySlider>
      <div class="col-span-12 mt-20 2xl:mt-auto 2xl:col-span-1 h-full 2xl:col-end-13">
        <form @submit.prevent="postNewConcurrencyLimit">
          <div class="h-full grid grid-cols-12 2xl:grid-cols-1 gap-4">
            <div class="col-span-6 2xl:col-span-1 2xl:h-64 items-center my-auto">
              <vue-slider
                  name="newLimit"
                  v-model="newLimit"
                  :direction="window.width > 1536 ? 'btt' : 'ltr'"
                  :drag-on-click="true"
                  :clickable="false"
                  :height="window.width > 1536 ? '100%' : ''"
                  :width="window.width > 1536 ? '' : '100%'"
                  :max="10"
                  :min="0"
                  class="m-auto 2xl:h-full"
              ></vue-slider>
            </div>
            <div class="col-span-4 2xl:col-span-1 2xl:h-8 content-center">
              <flat-pickr
                  class="form-control m-auto"
                  name="newAfterTime"
                  id="d3"
                  placeholder="hh:mm"
                  v-model="newAfterTime"
                  :config="{ enableTime: true, noCalendar: true, dateFormat: 'H:i', time_24hr: true }"
              >
              </flat-pickr>
            </div>
            <div class="col-span-2 2xl:col-span-1 2xl:h-8 content-center">
              <Button type="submit" class="btn btn-sm btn-dark block w-full text-center m-auto">
                Add
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
    <ConcurrencyLimitsSkeleton v-else :count="6"></ConcurrencyLimitsSkeleton>
  </Card>
</template>

<style scoped lang="scss">

</style>
