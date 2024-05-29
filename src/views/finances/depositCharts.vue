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
      interval: 'monthly',
      gracePeriod: 182,
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
            colors: '#CBD5E1',
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
              colors: '#CBD5E1',
            },
          },
          axisTicks: {
            color: '#CBD5E1',
          },
        },
        yaxis: {
          show: true,
          labels: {
            style: {
              colors: '#CBD5E1',
            },
            formatter: (val) => (`\u00A3${val}`),
          },
          axisTicks: {
            color: '#CBD5E1',
          },
          title: {
            text: 'Value of Deposits',
            style: {
              color: '#CBD5E1',
            },
          },
        },
      },
      totalDepositsSeries: [],
      claimableDepositsSeries: [],
      depositsCollectedSeries: [],
      depositsReturnedSeries: [],
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
    fetchTotalDepositsSeries() {
      requests.getTotalDepositsDateSeries(this.interval, this.startDate, this.endDate).then((response) => {
        this.totalDepositsSeries = response.data;
        this.updateStartDate(this.totalDepositsSeries[0].data[0][0]);
        this.updateEndDate(this.totalDepositsSeries[0].data[this.totalDepositsSeries[0].data.length -1][0]);
      });
    },
    fetchClaimableDepositsSeries() {
      requests.getClaimableDepositsDateSeries(this.interval, this.gracePeriod, this.startDate, this.endDate).then((response) => {
        this.claimableDepositsSeries = response.data;
        this.updateStartDate(this.claimableDepositsSeries[0].data[0][0]);
        this.updateEndDate(this.claimableDepositsSeries[0].data[this.claimableDepositsSeries[0].data.length -1][0]);
      });
    },
    fetchDepositsCollectedSeries() {
      requests.getDepositsCollectedDateSeries(this.interval, this.startDate, this.endDate).then((response) => {
        this.depositsCollectedSeries = response.data;
        this.updateStartDate(this.depositsCollectedSeries[0].data[0][0]);
        this.updateEndDate(this.depositsCollectedSeries[0].data[this.depositsCollectedSeries[0].data.length -1][0]);
      });
    },
    fetchDepositsReturnedSeries() {
      requests.getDepositsReturnedDateSeries(this.interval, this.startDate, this.endDate).then((response) => {
        this.depositsReturnedSeries = response.data;
        this.updateStartDate(this.depositsReturnedSeries[0].data[0][0]);
        this.updateEndDate(this.depositsReturnedSeries[0].data[this.depositsReturnedSeries[0].data.length -1][0]);
      });
    },
    fetchAllSeries() {
      this.fetchTotalDepositsSeries();
      this.fetchClaimableDepositsSeries();
      this.fetchDepositsCollectedSeries();
      this.fetchDepositsReturnedSeries();
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
      if (oldStartDate !== null && newStartDate !== oldStartDate) {
        this.fetchAllSeries();
      }
    },
    endDate(newEndDate, oldEndDate) {
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
          <div class="col-span-12 lg:col-span-6 items-center my-auto">
            <label class="text-slate-700 dark:text-slate-300">Granularity</label>
            <vue-slider
                :data="['daily', 'weekly', 'fortnightly', 'monthly', 'quarterly', 'semiyearly', 'yearly']"
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
          <div class="col-span-12 lg:col-span-6 items-center my-auto">
            <label class="text-slate-700 dark:text-slate-300">Grace Period (Days)</label>
            <vue-slider
                name="gracePeriod"
                v-model="gracePeriod"
                direction="ltr"
                :drag-on-click="true"
                :clickable="false"
                width="100%"
                :max="371"
                :min="0"
                :interval="7"
                class="m-auto"
                @drag-end="fetchClaimableDepositsSeries"
            ></vue-slider>
          </div>
          <div class="col-span-12 lg:col-span-6 content-center">
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
          <div class="col-span-12 lg:col-span-6 content-center">
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
    <div class="col-span-12 lg:col-span-6">
      <Card title="Total Deposits Collected">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="totalDepositsSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-6">
      <Card title="Claimable Deposits">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="claimableDepositsSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-6">
      <Card title="Collected Deposits">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="depositsCollectedSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-6">
      <Card title="Returned Deposits">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="depositsReturnedSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style lang="scss">
</style>
