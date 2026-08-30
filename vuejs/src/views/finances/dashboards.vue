<script setup>
import 'vue-slider-component/theme/antd.css';
import {ref, computed, watch} from 'vue';
import Card from '@/components/Card/index.vue';
import {useThemeSettingsStore} from '@/store/themeSettings';
import Select from '@/components/Select/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import VueSlider from 'vue-slider-component';
import DashButton from '@/components/Button/index.vue';

const toast = useToast();

const themeSettingsStore = useThemeSettingsStore();

const dashboards = ref([]);
const dashboardData = ref(null);
const selectedDashboard = ref(-1);
const startDate = ref((new Date()).toISOString().split('T')[0]);
const endDate = ref((new Date()).toISOString().split('T')[0]);
const interval = ref('monthly');
const intervalLabels = ref(['daily', 'weekly', 'fortnightly', 'monthly', 'quarterly', 'semiyearly', 'yearly']);
const dashboardParts = ref([]);


requests.getDashboards().then((response) => {
  dashboards.value = response.data.map((dashboard) => {
    return {
      name: dashboard.name,
      layout: JSON.parse(dashboard.layout),
    };
  });
});


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
  console.log('fetchDashboard', selectedDashboard.value);
  if (selectedDashboard.value < 0) {
    return;
  }
  
  const dashboard = dashboards.value[selectedDashboard.value];
  const dashboardQueries = dashboard.layout.map((layout) => layout.query);
  console.log('dashboardQueries', JSON.stringify(dashboardQueries));
  const queryString = JSON.stringify(dashboardQueries).replaceAll('#startdate#', startDate.value)
    .replaceAll('#enddate#', endDate.value)
    .replaceAll('#interval#', interval.value);
  console.log('queryString', queryString.replaceAll('#startdate#', startDate.value));
  
  const dashboardQuery = {
    name: 'My Dashboard',
    queries: JSON.parse(queryString),
  };
  
  console.log('dashboardQuery', dashboardQueries);

  dashboardParts.value = null;

  requests.getDashboard(dashboardQuery)
    .then(
      (response) => {
        dashboardData.value = response.data;
        console.log('dashboardData', response.data);

        dashboardParts.value = response.data.parts.map((dashboardDataPart, index) => {
          console.log('chart options', dashboard.layout[index].chartOptions);
          return {
            name: dashboardDataPart.name,
            chartOptions: dashboard.layout[index].chartOptions,
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
                ).toSorted((a, b) => Date.parse(a.x) - Date.parse(b.x)),
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
      v-if="dashboardParts"
      class="col-span-full grid grid-cols-12 gap-5"
    >
      <div
        v-for="dashboardPart in dashboardParts"
        :key="dashboardPart.name"
        class="col-span-12 lg:col-span-6"
      >
        <Card :title=dashboardPart.name>
          <template #header>
            <DashButton class="btn-sm" text="Edit Data"/>
            <DashButton class="btn-sm mx-5" text="Edit Chart"/>
          </template>
          <div class="grid grid-cols-12 gap-5">
            <div class="col-span-full">
              <apexchart
                @zoomed="handleSelection"
                class="text-slate-700 dark:text-slate-300"
                :type="dashboardPart.chartOptions.chart.type"
                :options="dashboardPart.chartOptions"
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
