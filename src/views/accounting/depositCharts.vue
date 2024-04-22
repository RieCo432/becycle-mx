<script>
import 'vue-slider-component/theme/antd.css';
import Card from '@/components/Card/index.vue';
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import requests from '@/requests';
export default {
  name: 'depositCharts',
  components: {
    Card,
    VueSlider,
  },
  data() {
    return {
      interval: 7,
      gracePeriod: 28,
      startDate: null,
      endDate: null,
      chartOptions: {
        chart: {
          type: 'area',
          height: 300,
          stacked: true,
        },
        theme: {
          mode: 'light',
        },
        dataLabels: {
          enabled: false,
        },
        stroke: {
          curve: 'smooth',
        },
        fill: {
          type: 'gradient',
          gradient: {
            opacityFrom: 0.6,
            opacityTo: 0.8,
          },
        },
        legend: {
          position: 'top',
          horizontalAlign: 'left',
          labels: {
            colors: ['#fffff'],
          },
        },
        tooltip: {
          theme: 'dark',
        },
        xaxis: {
          show: true,
          type: 'datetime',
          labels: {
            style: {
              color: '#ffffff',
            },
          },
          axisTicks: {
            color: '#ffffff',
          },
        },
        yaxis: {
          show: true,
          labels: {
            style: {
              color: '#ffffff',
            },
          },
          axisTicks: {
            color: '#ffffff',
          },
        },
      },
      totalDepositsCollectedSeries: [],
      claimableDepositsSeries: [],
    };
  },
  methods: {
    updateStartDate(newStartDate) {
      const newStartDateParsed = new Date(Date.parse(newStartDate));
      const oldStartDateParsed = this.startDate ? new Date(Date.parse(this.startDate)) : null;
      console.log('updateStartDate', newStartDate, this.startDate);
      if (!oldStartDateParsed || newStartDateParsed < oldStartDateParsed) {
        console.log('updating');
        this.startDate = newStartDate;
      }
    },
    updateEndDate(newEndDate) {
      const newEndDateParsed = new Date(Date.parse(newEndDate));
      const oldEndDateParsed = this.endDate ? new Date(Date.parse(this.endDate)) : null;
      if (!oldEndDateParsed || newEndDateParsed > oldEndDateParsed) {
        this.endDate = newEndDate;
      }
    },
    fetchTotalDepositsCollectedSeries() {
      requests.getTotalDepositsCollectedDateSeries(this.interval, this.startDate, this.endDate).then((response) => {
        this.totalDepositsCollectedSeries = response.data;
        this.updateStartDate(this.totalDepositsCollectedSeries[0].data[0][0]);
        this.updateEndDate(this.totalDepositsCollectedSeries[0].data[this.totalDepositsCollectedSeries[0].data.length -1][0]);
      });
    },
    fetchClaimableDepositsSeries() {
      requests.getClaimableDepositsDateSeries(this.interval, this.gracePeriod, this.startDate, this.endDate).then((response) => {
        this.claimableDepositsSeries = response.data;
        this.updateStartDate(this.claimableDepositsSeries[0].data[0][0]);
        this.updateEndDate(this.claimableDepositsSeries[0].data[this.claimableDepositsSeries[0].data.length -1][0]);
      });
    },
    fetchAllSeries() {
      this.fetchTotalDepositsCollectedSeries();
      this.fetchClaimableDepositsSeries();
    },
    handleSelection(chart, {xaxis, yaxis}) {
      if (xaxis.min) {
        const newStartDate = new Date(xaxis.min);
        this.startDate = `${newStartDate.getUTCFullYear()}-${(newStartDate.getUTCMonth() + 1).toString().padStart(2, '0')}-${newStartDate.getUTCDate().toString().padStart(2, '0')}`;
      } else {
        this.startDate = null;
      }
      if (xaxis.max) {
        const newEndDate = new Date(xaxis.max);
        this.endDate = `${newEndDate.getUTCFullYear()}-${(newEndDate.getUTCMonth() + 1).toString().padStart(2, '0')}-${newEndDate.getUTCDate().toString().padStart(2, '0')}`;
      } else {
        this.endDate = null;
      }
      this.fetchAllSeries();
    },
  },
  watch: {
    startDate(newStartDate, oldStartDate) {
      console.log(newStartDate, oldStartDate);
      if (oldStartDate !== null && newStartDate !== oldStartDate) {
        this.fetchAllSeries();
      }
    },
    endDate(newEndDate, oldEndDate) {
      console.log(newEndDate, oldEndDate);
      if (oldEndDate !== null && newEndDate !== oldEndDate) {
        this.fetchAllSeries();
      }
    },
  },
  created() {
    this.fetchAllSeries();
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card title="Controls">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-6 items-center my-auto">
            <label class="text-slate-700 dark:text-slate-300">Granularity (Days)</label>
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
                @drag-end="fetchAllSeries"
            ></vue-slider>
          </div>
          <div class="col-span-6 items-center my-auto">
            <label class="text-slate-700 dark:text-slate-300">Grace Period (Days)</label>
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
                @drag-end="fetchClaimableDepositsSeries"
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
                ref="startDatePicker"
                :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
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
            >
            </flat-pickr>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-6">
      <Card title="Total Deposits Collected">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="totalDepositsCollectedSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-6">
      <Card title="Claimable Deposits">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="claimableDepositsSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style lang="scss">
</style>
