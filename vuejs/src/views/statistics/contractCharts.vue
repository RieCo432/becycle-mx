<script>
import 'vue-slider-component/theme/antd.css';
import Card from '@/components/Card/index.vue';
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import requests from '@/requests';
import {useThemeSettingsStore} from '@/store/themeSettings';
import dateUtils from '@/util/dateUtils';
import Icon from '@/components/Icon/index.vue';
import DashButton from '@/components/Button/index.vue';

const themeSettingsStore = useThemeSettingsStore();

// Default period is the current financial year
const financialYear = dateUtils.getFinancialYear();

const initialStartDate = dateUtils.convertDateToPickerString(financialYear.start);
const initialEndDate = dateUtils.convertDateToPickerString(financialYear.end);


export default {
  name: 'contractCharts',
  components: {
    DashButton, Icon,
    Card,
    VueSlider,
  },
  data() {
    return {
      interval: 'monthly',
      gracePeriod: 182,
      startDate: initialStartDate,
      endDate: initialEndDate,
      chartOptions: {
        chart: {
          type: 'area',
          height: 300,
          stacked: true,
          zoom: {
            enabled: false,
            allowMouseWheelZoom: false,
          },
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
          theme: themeSettingsStore.theme,
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
          },
          axisTicks: {
            color: '#CBD5E1',
          },
          title: {
            text: 'Number of Contracts',
            style: {
              color: '#CBD5E1',
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
          show: true,
          position: 'bottom',
          fontSize: '16px',
          fontFamily: 'Inter',
          fontWeight: 400,
          horizontalAlign: 'left',
          clusterGroupedSeriesOrientation: 'vertical',
          height: '100px',
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
    fetchTotalContractsSeries() {
      requests.getTotalContractsDateSeries(this.interval, this.startDate, this.endDate)
        .then((response) => {
          this.totalContractSeries = response.data;
        });
    },
    fetchActiveContractsSeries() {
      requests.getActiveContractsDateSeries(this.interval, this.gracePeriod, this.startDate, this.endDate)
        .then((response) => {
          this.activeContractSeries = response.data;
        });
    },
    fetchNewContractsSeries() {
      requests.getNewContractsDateSeries(this.interval, this.startDate, this.endDate)
        .then((response) => {
          this.newContractSeries = response.data;
        });
    },
    fetchReturnedContractsSeries() {
      requests.getReturnedContractsDateSeries(this.interval, this.startDate, this.endDate)
        .then((response) => {
          this.returnedContractSeries = response.data;
        });
    },
    fetchContractsStatus() {
      requests.getContractsStatus(this.gracePeriod, this.startDate, this.endDate)
        .then((response) => {
          this.contractsStatusChartOptions.labels
            .splice(0, this.contractsStatusChartOptions.labels.length, ...Object.keys(response.data));
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
    changeYear(delta) {
      const end = new Date(this.endDate);
      const start = new Date(this.startDate);

      end.setUTCFullYear(end.getUTCFullYear() + delta);
      start.setUTCFullYear(start.getUTCFullYear() + delta);

      this.endDate = dateUtils.convertDateToPickerString(end);
      this.startDate = dateUtils.convertDateToPickerString(start);
    },
  },
  watch: {
    startDate() {
      this.fetchAllSeries();
    },
    endDate() {
      this.fetchAllSeries();
    },
  },
  created() {
    this.fetchAllSeries();
  },
};
</script>

<template>
  <div class="grid grid-cols-12 lg:grid-cols-8 2xl:grid-cols-10 gap-5">
    <div class="col-span-full 2xl:col-span-2">
      <Card title="Controls">
        <div class="grid grid-cols-1 gap-5">
          <div class="col-span-1 items-center my-auto">
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
          <div class="col-span-1 items-center my-auto">
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
          <div class="col-span-1 items-center my-auto">
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
          <div class="col-span-1 items-center my-auto">
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
          <div class="col-span-1 grid grid-cols-2 gap-5">
            <DashButton
              class="btn-sm mx-5"
              @click="changeYear(-1)">
              <Icon icon="heroicons-outline:chevron-left"/>
            </DashButton>
            <DashButton
              class="btn-sm mx-5"
              @click="changeYear(1)">
              <Icon icon="heroicons-outline:chevron-right"/>
            </DashButton>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-4">
      <Card title="Total Contracts">
        <apexchart
          class="text-slate-700 dark:text-slate-300"
          type="area"
          :options="chartOptions"
          :series="totalContractSeries"/>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-4">
      <Card title="Active Contracts">
        <apexchart
          class="text-slate-700 dark:text-slate-300"
          type="area"
          :options="chartOptions"
          :series="activeContractSeries"/>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-4 2xl:col-span-2 row-start-6 lg:row-start-4 2xl:row-start-2 min-h-96">
      <Card title="Contracts Status" className="h-full">
        <apexchart
          class="text-slate-700 dark:text-slate-300 w-full h-full"
          type="donut"
          height="100%"
          width="100%"
          :options="contractsStatusChartOptions"
          :series="contractsStatusSeries"/>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-4">
      <Card title="New Contracts">
        <apexchart
          class="text-slate-700 dark:text-slate-300"
          type="area"
          :options="chartOptions"
          :series="newContractSeries"/>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-4">
      <Card title="Returned Contracts">
        <apexchart
          class="text-slate-700 dark:text-slate-300"
          type="area"
          :options="chartOptions"
          :series="returnedContractSeries"/>
      </Card>
    </div>
  </div>
</template>

<style lang="scss">
</style>
