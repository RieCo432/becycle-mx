<script>
import Card from '@/components/Card/index.vue';
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import chartOptions from '@/constant/stackedAreaChartOptions';
import requests from '@/requests';

export default {
  name: 'ActiveContractsDateSeriesCard',
  components: {Card, VueSlider},
  data() {
    return {
      series: [],
      interval: 7,
      gracePeriod: 28,
      chartOptions: chartOptions,
    };
  },
  methods: {
    fetchDateSeries() {
      requests.getActiveContractsDateSeries(this.interval, this.gracePeriod).then((response) => {
        this.series = response.data;
      });
    },
  },
  created() {
    this.fetchDateSeries();
  },
};
</script>

<template>
  <Card title="Active Contracts">
    <div class="grid grid-cols-12 gap-5">
      <div class="col-span-full">
        <apexchart class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="series"></apexchart>
      </div>
      <div class="col-span-6 items-center my-auto">
        <label class="text-slate-700 dark:text-slate-300">Interval</label>
        <vue-slider
            name="interval"
            v-model="interval"
            direction="ltr"
            :drag-on-click="true"
            :clickable="false"
            width="100%"
            :max="56"
            :min="0"
            :interval="7"
            class="m-auto"
            @update:modelValue="fetchDateSeries"
        ></vue-slider>
      </div>
      <div class="col-span-6 items-center my-auto">
        <label class="text-slate-700 dark:text-slate-300">Grace Period</label>
        <vue-slider
            name="gracePeriod"
            v-model="gracePeriod"
            direction="ltr"
            :drag-on-click="true"
            :clickable="false"
            width="100%"
            :max="182"
            :min="0"
            :interval="7"
            class="m-auto"
            @update:modelValue="fetchDateSeries"
        ></vue-slider>
      </div>
    </div>
  </Card>
</template>

<style scoped lang="scss">

</style>