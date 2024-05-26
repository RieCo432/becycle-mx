<script>
import 'vue-slider-component/theme/antd.css';
import Card from '@/components/Card/index.vue';
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import requests from '@/requests';
export default {
  name: 'contractCharts',
  components: {
    Card,
    VueSlider,
  },
  data() {
    return {
      interval: 'monthly',
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
              colors: '#dddddd',
            },
          },
          axisTicks: {
            color: '#dddddd',
          },
        },
        yaxis: {
          show: true,
          labels: {
            style: {
              colors: '#dddddd',
            },
          },
          axisTicks: {
            color: '#dddddd',
          },
          title: {
            text: 'Number of Contracts',
            style: {
              color: '#dddddd',
            },
          },
        },
      },
      contractsStatusChartOptions: {
        labels: [],
        colors: ['#4669FA', '#FA916B', '#50C793', '#0CE7FA'],
        dataLabels: {
          enabled: true,
        },
        legend: {
          position: 'bottom',
          fontSize: '16px',
          fontFamily: 'Inter',
          fontWeight: 400,
          labels: {
            colors: '#CBD5E1',
          },
        },
        chart: {
          toolbar: {
            show: false,
          },
        },
        plotOptions: {
          pie: {
            donut: {
              labels: {
                show: true,
                name: {
                  show: true,
                  fontSize: '20px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#CBD5E1',
                  formatter: (s) => (s.replaceAll('_', ' ')),
                },
                value: {
                  show: true,
                  fontSize: '16px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#CBD5E1',
                },
                total: {
                  show: true,
                  fontSize: '20px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#CBD5E1',
                },
              },
            },
          },
        },
      },
      totalContractSeries: [],
      activeContractSeries: [],
      newContractSeries: [],
      returnedContractSeries: [],
      contractsStatusSeries: [],
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
    fetchTotalContractsSeries() {
      requests.getTotalContractsDateSeries(this.interval, this.startDate, this.endDate).then((response) => {
        this.totalContractSeries = response.data;
        this.updateStartDate(this.totalContractSeries[0].data[0][0]);
        this.updateEndDate(this.totalContractSeries[0].data[this.totalContractSeries[0].data.length -1][0]);
      });
    },
    fetchActiveContractsSeries() {
      requests.getActiveContractsDateSeries(this.interval, this.gracePeriod, this.startDate, this.endDate).then((response) => {
        this.activeContractSeries = response.data;
        this.updateStartDate(this.activeContractSeries[0].data[0][0]);
        this.updateEndDate(this.activeContractSeries[0].data[this.activeContractSeries[0].data.length -1][0]);
      });
    },
    fetchNewContractsSeries() {
      requests.getNewContractsDateSeries(this.interval, this.startDate, this.endDate).then((response) => {
        this.newContractSeries = response.data;
        this.updateStartDate(this.newContractSeries[0].data[0][0]);
        this.updateEndDate(this.newContractSeries[0].data[this.newContractSeries[0].data.length -1][0]);
      });
    },
    fetchReturnedContractsSeries() {
      requests.getReturnedContractsDateSeries(this.interval, this.startDate, this.endDate).then((response) => {
        this.returnedContractSeries = response.data;
        this.updateStartDate(this.returnedContractSeries[0].data[0][0]);
        this.updateEndDate(this.returnedContractSeries[0].data[this.returnedContractSeries[0].data.length -1][0]);
      });
    },
    fetchContractsStatus() {
      requests.getContractsStatus(this.gracePeriod, this.startDate, this.endDate).then((response) => {
        this.contractsStatusChartOptions.labels.splice(0, this.contractsStatusChartOptions.labels.length, ...Object.keys(response.data));
        this.contractsStatusSeries = Object.values(response.data);
      });
    },
    fetchAllSeries() {
      this.fetchTotalContractsSeries();
      this.fetchActiveContractsSeries();
      this.fetchNewContractsSeries();
      this.fetchReturnedContractsSeries();
      this.fetchContractsStatus();
    },
    fetchGracePeriodDependants() {
      this.fetchContractsStatus();
      this.fetchActiveContractsSeries();
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
          <div class="col-span-6 items-center my-auto">
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
          <div class="col-span-6 items-center my-auto">
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
                @drag-end="fetchGracePeriodDependants"
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
      <Card title="Total Contracts">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="totalContractSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-6">
      <Card title="Active Contracts">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="activeContractSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-6">
      <Card title="New Contracts">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="newContractSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-6">
      <Card title="Returned Contracts">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart class="text-slate-700 dark:text-slate-300" type="area" :options="chartOptions" :series="returnedContractSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-4">
      <Card title="Contracts Status">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="donut" :options="contractsStatusChartOptions" :series="contractsStatusSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
  </div>

</template>

<style lang="scss">
</style>
