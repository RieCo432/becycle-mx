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
import Icon from '@/components/Icon';
import DashboardQueryEditor from '@/components/Editors/DashboardQueryEditor.vue';
import TextArea from '@/components/TextArea/index.vue';
import Switch from '@/components/Switch/index.vue';

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


function parseDashboard(dashboard) {
  return {
    id: dashboard.id,
    name: dashboard.name,
    layout: JSON.parse(dashboard.layout),
  };
}


requests.getDashboards().then((response) => {
  dashboards.value = response.data.map((dashboard) => (parseDashboard(dashboard)));
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

const editDataSource = ref(null);
const editChartOptions = ref(null);
const editingIndex = ref(null);
const currentlyEditing = ref(null);


function startEdit(index) {
  editingIndex.value = index;
  editDataSource.value = dashboards.value[selectedDashboard.value].layout[index].query;
  editChartOptions.value = JSON.stringify(dashboards.value[selectedDashboard.value].layout[index].chartOptions, null, 2);
}

function editData(index) {
  startEdit(index);
  currentlyEditing.value = 'query';
}

function editChart(index) {
  startEdit(index);
  currentlyEditing.value = 'options';
}

function resetEditing() {
  editingIndex.value = null;
  currentlyEditing.value = null;
  editDataSource.value = null;
  editChartOptions.value = null;
}

function cancelChanges() {
  resetEditing();
  toast.error('Changes canceled', {timeout: 2000});
}

function saveChanges() {
  console.log('saving changes', editDataSource.value, editChartOptions.value);
  dashboards.value[selectedDashboard.value].layout[editingIndex.value].query = editDataSource.value;
  dashboards.value[selectedDashboard.value].layout[editingIndex.value].chartOptions = JSON.parse(editChartOptions.value);

  console.log('dashboard layout', dashboards.value[selectedDashboard.value].layout);

  const newLayout = JSON.stringify(dashboards.value[selectedDashboard.value].layout);
  console.log('dashboard id', dashboards.value[selectedDashboard.value].id);

  requests.putDashboardUpdate(dashboards.value[selectedDashboard.value].id, {name: dashboards.value[selectedDashboard.value].name, layout: newLayout})
    .then((response) => {
      dashboards.value.splice(selectedDashboard.value, 1, parseDashboard(response.data));
      toast.success('Changes saved', {timeout: 2000});
      fetchDashboard();
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });


  resetEditing();
}

function addDashboardPart() {
  dashboards.value[selectedDashboard.value].layout.push({
    query: {
      name: 'New graph',
      series: [],
      startDate: '#startdate#',
      endDate: '#enddate#',
      interval: '#interval#',
      mode: 'period',
      dimension: 'cashflow',
      fundId: null,
    },
    chartOptions: {
      chart: {
        type: 'area',
      },
    },
  });
  console.log('layout', dashboards.value[selectedDashboard.value].layout);
  editData(dashboards.value[selectedDashboard.value].layout.length - 1);
  console.log('editDataSource', dashboards.value[selectedDashboard.value].layout[editingIndex.value].query.name);
}

const editingModeRaw = ref(false);

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
      v-if="dashboardParts && dashboardParts.length"
      class="col-span-full grid grid-cols-12 gap-5"
    >
      <template
        v-for="(dashboardPart, index) in dashboardParts"
        :key="dashboardPart.name"
      >
        <template v-if="editingIndex === null || editingIndex === index">
          <div class="col-span-12 lg:col-span-4">
            <Card :title=dashboardPart.name>
              <template #header>
                <DashButton class="btn-sm mx-5" text="Edit Data" @click="editData(index)"/>
                <DashButton class="btn-sm mx-5" text="Edit Chart" @click="editChart(index)"/>
              </template>
              <div class="grid grid-cols-12 gap-5">
                <div class="col-span-full">
                  <apexchart
                    @zoomed="handleSelection"
                    class="text-slate-700 dark:text-slate-300"
                    :options="dashboardPart.chartOptions"
                    :series="dashboardPart.series"></apexchart>
                </div>
              </div>
            </Card>
          </div>

        </template>
      </template>


      <template v-if="editingIndex !== null && currentlyEditing === 'query'">
        <div class="col-span-12 lg:col-span-4">
          <Card :title="`Editing Query for ${dashboards[selectedDashboard].layout[editingIndex].query.name}`">
            <template #header>
              <div class="grid grid-cols-3">
                <div class="pt-1">
                  <Switch class="d-inline-block mt-4" v-model="editingModeRaw" label="Raw"/>
                </div>
                <DashButton class="btn-sm mx-5 dark:btn-success" text="Save" @click="saveChanges"/>
                <DashButton class="btn-sm mx-5 dark:btn-danger" text="Cancel" @click="cancelChanges"/>
              </div>
            </template>
            <div class="w-full h-full" v-if="!editingModeRaw">
              <DashboardQueryEditor v-model="editDataSource"/>
            </div>
            <div
              class="w-full h-full"
              v-if="editingModeRaw">
              <TextArea
                classInput="w-full h-full"
                :modelValue="JSON.stringify(editDataSource, null, 2)"
                @update:modelValue="(v) => editDataSource = JSON.parse(v)"
              ></TextArea>
            </div>
          </Card>
        </div>
      </template>


      <template v-if="editingIndex !== null  && currentlyEditing === 'options'">
        <div class="col-span-12 lg:col-span-4">
          <Card :title="`Editing Chart Options for ${dashboards[selectedDashboard].layout[editingIndex].query.name}`">
            <template #header>
              <DashButton class="btn-sm mx-5 dark:btn-success" text="Save" @click="saveChanges"/>
              <DashButton class="btn-sm mx-5 dark:btn-danger" text="Cancel" @click="cancelChanges"/>
            </template>
            <textarea
              class="w-full h-full"
              v-model="editChartOptions"
              placeholder="Enter your chart options here"
            ></textarea>
          </Card>
        </div>
      </template>
      <template v-if="editingIndex !== null  && currentlyEditing === 'options'">
        <div class="col-span-12 lg:col-span-4">
          <Card :title="`Editing Chart Options for ${dashboards[selectedDashboard].layout[editingIndex].query.name}`">
            <template #header>
              <DashButton class="btn-sm mx-5 dark:btn-success" text="Save" @click="saveChanges"/>
              <DashButton class="btn-sm mx-5 dark:btn-danger" text="Cancel" @click="cancelChanges"/>
            </template>
            <textarea
              class="w-full h-full"
              v-model="editChartOptions"
              placeholder="Enter your chart options here"
            ></textarea>
          </Card>
        </div>
      </template>

      <div v-if="editingIndex === null" class="col-span-12 lg:col-span-4">
        <DashButton
          class="btn-dark h-full w-full"
          @click="addDashboardPart"
        >
          <Icon icon="heroicons-outline:plus"/>
        </DashButton>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
