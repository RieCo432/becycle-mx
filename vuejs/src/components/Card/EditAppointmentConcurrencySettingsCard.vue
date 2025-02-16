<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import AppointmentConcurrencySlider from '@/components/Slider/AppointmentConcurrencySlider.vue';
import {useToast} from 'vue-toastification';
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import Button from '@/components/Button/index.vue';
import window from '@/mixins/window';
import Select from '@/components/Select/index.vue';
import {number} from 'yup';

const toast = useToast();

export default {
  name: 'EditAppointmentConcurrencySettingsCard',
  mixins: [window],
  components: {
    Select,
    Button,
    AppointmentConcurrencySlider,
    Card,
    VueSlider,
  },
  data() {
    return {
      newWeekDay: this.weekDay,
      newAfterTime: null,
      newLimit: 0,
    };
  },
  props: {
    weekDay: {
      type: number,
      required: true,
    },
    weekDayOptions: {
      type: Array,
      required: true,
    },
    concurrencyLimits: {
      type: Array,
      required: true,
    },
    weekDayName: {
      type: String,
      required: true,
    },
  },
  emits: [
    'concurrencyLimitAdjusted',
    'concurrencyLimitDeleted',
    'concurrencyLimitAdded',
  ],
  methods: {
    postNewConcurrencyLimit() {
      if (this.newWeekDay == null || this.newAfterTime == null) {
        toast.error('You must choose a week day and time!', {timeout: 2000});
      } else {
        requests.postNewAppointmentConcurrencyLimit({
          weekDay: parseInt(this.newWeekDay),
          afterTime: this.newAfterTime.concat(':00'),
          maxConcurrent: this.newLimit,
        }).then((response) => {
          this.$emit('concurrencyLimitAdded', response.data);
          toast.success('Appointment Concurrency Limit added', {timeout: 2000});
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        }).finally(() => {
          this.newWeekDay = this.weekDay;
          this.newLimit = 0;
          this.newAfterTime = null;
        });
      }
    },
  },
};
</script>

<template>
  <Card :title="`Appointment Limits for ${weekDayName}`">
    <div class="grid grid-cols-12 2xl:grid-cols-8 gap-5 h-full">
        <AppointmentConcurrencySlider
            v-for="concurrencyLimit in concurrencyLimits"
            :concurrency-limit="concurrencyLimit"
            :key="`${concurrencyLimit.weekDay}${concurrencyLimit.afterTime}`"
            :week-day-options="weekDayOptions"
            @concurrency-limit-adjusted="(updatedConcurrencyLimit) =>
            $emit('concurrencyLimitAdjusted', concurrencyLimit.weekDay, concurrencyLimit.afterTime, updatedConcurrencyLimit)"
            @concurrency-limit-deleted="$emit('concurrencyLimitDeleted', concurrencyLimit.weekDay, concurrencyLimit.afterTime)"
            class="h-full"
        ></AppointmentConcurrencySlider>
      <div class="col-span-12 mt-20 2xl:mt-auto 2xl:col-span-1 h-full 2xl:col-end-9">
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
            <div class="col-span-2 2xl:col-span-1 2xl:h-8 content-center">
              <Select
                  placeholder="Day"
                  :options="weekDayOptions"
                  v-model="newWeekDay"
                  name="weekDay"
              />
            </div>
            <div class="col-span-2 2xl:col-span-1 2xl:h-8 content-center">
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
  </Card>
</template>

<style scoped lang="scss">

</style>
