<script>
import Card from '@/components/Card/index.vue';
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import chartOptions from '@/constant/stackedAreaChartOptions';
import requests from '@/requests';

export default {
  name: 'NewContractsDateSeriesCard',
  components: {Card, VueSlider},
  data() {
    return {
      series: [],
      startDate: null,
      endDate: null,
      interval: 7,
      chartOptions: chartOptions,
    };
  },
  methods: {
    fetchDateSeries() {
      requests.getNewContractsDateSeries(this.interval, this.startDate, this.endDate).then((response) => {
        this.series = response.data;
        if (!this.startDate) {
          this.startDate = new Date(Date.parse(this.series[0].data[0][0]));
        }
        if (!this.endDate) {
          this.endDate = new Date(Date.parse(this.series[0].data[this.series[0].data.length - 1][0]));
        }
      });
    },
  },
  created() {
    this.fetchDateSeries();
  },
};
</script>

<template>
  <Card title="New Contracts">
    <div class="grid grid-cols-12 gap-5">
      <div class="col-span-full">
        <apexchart class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="series"></apexchart>
      </div>
      <div class="col-span-full items-center my-auto">
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
      <div class="col-span-4 content-center">
        <label class="text-slate-700 dark:text-slate-300">Period Start</label>
        <flat-pickr
            class="form-control m-auto"
            name="startDate"
            id="d3"
            placeholder="dd-mm-yyyy"
            v-model="startDate"
            :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
            @change="fetchDateSeries"
        >
        </flat-pickr>
      </div>
      <div class="col-span-4 content-center">
        <label class="text-slate-700 dark:text-slate-300">Period End</label>
        <flat-pickr
            class="form-control m-auto"
            name="endDate"
            id="d3"
            placeholder="dd-mm-yyyy"
            v-model="endDate"
            :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
            @change="fetchDateSeries"
        >
        </flat-pickr>
      </div>
    </div>
  </Card>
</template>

<style scoped lang="scss">

</style>