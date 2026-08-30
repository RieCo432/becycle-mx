<script setup>
import 'vue-slider-component/theme/antd.css';
import {ref, computed, watch} from 'vue';
import Card from '@/components/Card/index.vue';
import {useThemeSettingsStore} from '@/store/themeSettings';
import Select from '@/components/Select/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import VueSlider from 'vue-slider-component';

const toast = useToast();

const themeSettingsStore = useThemeSettingsStore();

function getChartOptions(type, yAxisLabel) {
  return {
    chart: {
      type: type,
      height: 300,
      zoom: {
        enabled: true,
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
      type: type === 'area' ? 'datetime' : 'category',
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
        formatter: (val) => (`\u00A3 ${val}`),
      },
      axisTicks: {
        color: '#CBD5E1',
      },
      title: {
        text: yAxisLabel,
        style: {
          color: '#CBD5E1',
        },
      },
    },
  };
}


const dashboards = ref([
  {
    name: 'My Dashboard',
    queries: [
      {
        name: 'First Graph',
        series: [
          {
            name: 'asset',
            query: 'asset',
          },
          {
            name: 'liability',
            query: 'liability',
          },
        ],
        dimension: 'balance',
        fundId: 'c96937cd-d61b-40dc-98b1-0dc21cac015f',
        mode: 'period',
        endDate: '#enddate#',
        startDate: '#startdate#',
        interval: '#interval#',
        type: 'area',
      },
      {
        name: 'Second Graph',
        series: [
          {
            name: 'asset',
            query: 'asset',
          },
          {
            name: 'liability',
            query: 'liability',
          },
        ],
        dimension: 'cashflow',
        fundId: 'c96937cd-d61b-40dc-98b1-0dc21cac015f',
        mode: 'period',
        endDate: '#enddate#',
        startDate: '#startdate#',
        interval: '#interval#',
        type: 'area',
      },
      {
        name: 'Third Graph',
        series: [
          {
            name: 'series 1',
            query: [
              'f8b20739-cc25-4d4b-9169-3591c5699a70',
              '50d8e47a-6fbb-4252-87ec-8f5714150b43',
              '07460f20-bcfa-45c3-b50e-06e1c082a3d8',
            ],
          },
          {
            name: 'series 2',
            query: [
              '40d232f8-ca8e-4066-900f-1a643f8a0c5a',
              '989b20ae-6902-484a-bb84-8476dc667509',
            ],
          },
        ],
        dimension: 'balance',
        fundId: 'c96937cd-d61b-40dc-98b1-0dc21cac015f',
        mode: 'moment',
        moment: '#enddate#',
        type: 'bar',
      },
    ],
  },
]);

const dashboardData = ref(null);
const selectedDashboard = ref(-1);
const startDate = ref((new Date()).toISOString().split('T')[0]);
const endDate = ref((new Date()).toISOString().split('T')[0]);
const interval = ref('monthly');
const intervalLabels = ref(['daily', 'weekly', 'fortnightly', 'monthly', 'quarterly', 'semiyearly', 'yearly']);



const seriesData = ref([]);

function handleSelection(chart, {xaxis}) {
  // if (xaxis.min) {
  //   const newStartDate = new Date(xaxis.min);
  //   this.startDate = `${newStartDate.getUTCFullYear()}-${(newStartDate.getUTCMonth() + 1).toString()
  //     .padStart(2, '0')}-${newStartDate.getUTCDate().toString().padStart(2, '0')}`;
  // } else {
  //   this.startDate = null;
  // }
  // if (xaxis.max) {
  //   const newEndDate = new Date(xaxis.max);
  //   this.endDate = `${newEndDate.getUTCFullYear()}-${(newEndDate.getUTCMonth() + 1).toString()
  //     .padStart(2, '0')}-${newEndDate.getUTCDate().toString().padStart(2, '0')}`;
  // } else {
  //   this.endDate = null;
  // }
  // this.fetchAllSeries();
}

watch(startDate, () => {
  fetchDashboard();
});
watch(endDate, () => {
  fetchDashboard();
});
watch(interval, () => {
  fetchDashboard();
});

function fetchDashboard() {
  console.log('fetchDashboard', interval.value, intervalLabels.value);
  const dashboardQueries = dashboards.value[selectedDashboard.value];

  requests.getDashboard(
    JSON.parse(
      JSON.stringify(dashboardQueries)
        .replaceAll('#startdate#', startDate.value)
        .replaceAll('#enddate#', endDate.value)
        .replaceAll('#interval#', interval.value),
    ),
  )
    .then(
      (response) => {
        dashboardData.value = response.data;

        seriesData.value = dashboardData.value.parts.map((dashboardDataPart, index) => {
          const chartType = dashboards.value[selectedDashboard.value].queries[index].type;
          return {
            name: dashboardDataPart.name,
            yAxisLabel: dashboards.value[selectedDashboard.value].queries[index].dimension,
            type: chartType,
            series: dashboardDataPart.series.map(
              (seriesData) => ({
                name: `${seriesData.name}${seriesData.meta?.flow? `_${seriesData.meta.flow}` : ''}`,
                data: seriesData.data.map(
                  (dataPoint) => (
                    {
                      x: dataPoint.date,
                      y: dataPoint.value / 100,
                    }
                  ),
                ),
              }),
            ),
          };
        });
      },
    )
    .catch(
      (error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      },
    );
}

</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card title="Controls">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-12 lg:col-span-6 items-center my-auto">
            <label class="text-slate-700 dark:text-slate-300">Dashboard</label>
            <Select
              :options="dashboards.map((dashboard, index) => ({
                label: dashboard.name,
                value: index,
              }))"
              name="dashboard"
              v-model="selectedDashboard"
              @change="fetchDashboard"
            ></Select>
          </div>
          <div class="col-span-12 lg:col-span-6 items-center my-auto">
            <label class="text-slate-700 dark:text-slate-300">Granularity</label>
            <vue-slider
              :data="intervalLabels"
              name="interval"
              v-model="interval"
              direction="ltr"
              :drag-on-click="true"
              :clickable="false"
              width="100%"
              :max="7"
              :min="0"
              :interval="1"
              class="m-auto"
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
    <div
      v-if="seriesData"
      class="col-span-full grid grid-cols-12 gap-5"
    >
      <div
        v-for="dashboardPart in seriesData"
        :key="dashboardPart.name"
        class="col-span-12 lg:col-span-6"
      >
        <Card :title=dashboardPart.name>
          <div class="grid grid-cols-12 gap-5">
            <div class="col-span-full">
              <apexchart
                @zoomed="handleSelection"
                class="text-slate-700 dark:text-slate-300"
                :type="dashboardPart.type"
                :options="getChartOptions(dashboardPart.type, dashboardPart.yAxisLabel, dashboardPart.series.map(seriesData => seriesData.name))"
                :series="dashboardPart.series"></apexchart>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
