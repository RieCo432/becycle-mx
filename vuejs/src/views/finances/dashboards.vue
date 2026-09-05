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
import TextArea from '@/components/Textarea/index.vue';
import Switch from '@/components/Switch/index.vue';
import DashboardChartEditor from '@/components/Editors/DashboardChartEditor.vue';

const toast = useToast();

const themeSettingsStore = useThemeSettingsStore();

const dashboards = ref([]);
const dashboardData = ref(null);
const selectedDashboard = ref(-1);
const d = new Date();
d.setMonth(d.getMonth()-5);
const endDate = ref((new Date()).toISOString().split('T')[0]);
const startDate = ref(d.toISOString().split('T')[0]);
const interval = ref('monthly');
const intervalLabels = ref(['daily', 'weekly', 'fortnightly', 'monthly', 'quarterly', 'semiyearly', 'yearly']);
const dashboardParts = ref([]);
const editMode = ref(false);


function parseDashboard(dashboard) {
  return {
    id: dashboard.id,
    name: dashboard.name,
    layout: JSON.parse(dashboard.layout),
  };
}

requests.getDashboards().then((response) => {
  dashboards.value = response.data.map((dashboard) => (parseDashboard(dashboard)));
  selectedDashboard.value = 0;
  fetchDashboard();
});

watch(startDate, () => {
  fetchDashboard();
});
watch(endDate, () => {
  fetchDashboard();
});
watch(interval, () => {
  fetchDashboard();
});

function getBlankChartOptions() {
  return {
    chart: {
      type: 'bar',
      zoom: {
        enabled: false,
        allowMouseWheelZoom: false,
      },
    },
    colors: [],
    dataLabels: {
      enabled: false,
    },
    plotOptions: {
      bar: {
        distributed: true,
      },
    },
    stroke: {
      curve: 'smooth',
    },
    fill: {
      type: 'solid',
      gradient: {
        opacityFrom: 0.6,
        opacityTo: 0.8,
      },
    },
    legend: {
      showForSingleSeries: true,
      position: 'right',
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
      convertedCatToNumeric: false,
      tickAmount: 'dataPoints',
    },
    yaxis: [
      {
        show: true,
        labels: {
          show: true,
          style: {
            colors: '#CBD5E1',
            fontSize: '11px',
            fontWeight: 400,
            cssClass: '',
          },
        },
        axisBorder: {
          show: false,
          color: '#e0e0e0',
          width: 1,
        },
        axisTicks: {
          show: false,
          color: '#CBD5E1',
          width: 6,
        },
        title: {
          text: 'cashflow',
          rotate: -90,
          style: {
            color: '#CBD5E1',
            fontSize: '11px',
            fontWeight: 900,
            cssClass: '',
          },
        },
        tooltip: {
          enabled: false,
        },
        crosshairs: {
          show: true,
          position: 'front',
          stroke: {
            color: '#b6b6b6',
            width: 1,
            dashArray: 0,
          },
        },
      },
    ],
  };
}

function fetchDashboard() {
  if (selectedDashboard.value < 0) {
    return;
  }

  const dashboard = dashboards.value[selectedDashboard.value];
  const dashboardQueries = dashboard.layout.map((layout) => layout.query);
  const queryString = JSON.stringify(dashboardQueries).replaceAll('#startdate#', startDate.value)
    .replaceAll('#enddate#', endDate.value)
    .replaceAll('#interval#', interval.value);

  const dashboardQuery = {
    name: 'My Dashboard',
    queries: JSON.parse(queryString),
  };

  function applyDefaultChartOptions(chartOptions) {
    chartOptions.yaxis[0].labels.formatter = (val) => (`\u00A3 ${val.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`);
    if (chartOptions?.tooltip?.theme) {
      chartOptions.tooltip.theme = themeSettingsStore.theme;
    }
    return chartOptions;
  }

  requests.getDashboard(dashboardQuery)
    .then(
      (response) => {
        dashboardData.value = response.data;
        dashboardParts.value.splice(0, dashboardParts.value.length, ...response.data.parts.map((dashboardDataPart, index) => {
          return {
            name: dashboardDataPart.name,
            chartOptions: applyDefaultChartOptions(dashboard.layout[index].chartOptions),
            series: dashboard.layout[index].query.mode === 'period' ?
              dashboardDataPart.series.map(
                (seriesData) => {
                  return {
                    name: `${seriesData.name}${seriesData.meta?.flow? `_${seriesData.meta.flow}` : ''}`,
                    data: seriesData.data.map(
                      (dataPoint) => (
                        {
                          x: new Date(dataPoint.date).getTime(),
                          y: dataPoint.value / 100,
                        }
                      ),
                    ).toSorted((a, b) => Date.parse(a.x) - Date.parse(b.x)),
                  };
                },
              ) :
              [{
                data: dashboardDataPart.series.map(
                  (seriesData) => (
                    {
                      x: seriesData.name,
                      y: seriesData.data[0].value / 100,
                    }
                  ),
                ),
              }],
          };
        }));
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
  editChartOptions.value = dashboards.value[selectedDashboard.value].layout[index].chartOptions;
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

function closeEditor() {
  resetEditing();
  toast.error('Changes canceled', {timeout: 2000});
}

function submitChanges() {
  const newLayout = JSON.stringify(dashboards.value[selectedDashboard.value].layout);

  requests.putDashboardUpdate(dashboards.value[selectedDashboard.value].id, {
    name: dashboards.value[selectedDashboard.value].name,
    layout: newLayout,
  })
    .then((response) => {
      dashboards.value.splice(selectedDashboard.value, 1, parseDashboard(response.data));
      toast.success('Changes saved', {timeout: 2000});
      fetchDashboard();
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });
}

function saveChanges() {
  dashboards.value[selectedDashboard.value].layout[editingIndex.value].query = editDataSource.value;
  dashboards.value[selectedDashboard.value].layout[editingIndex.value].chartOptions = editChartOptions.value;

  submitChanges();
  // resetEditing();
}

function livePreviewChartOptions(chartOptions) {
  if (dashboardParts.value &&
    editingIndex.value >= 0 &&
    dashboardParts.value[editingIndex.value]
  ) {
    dashboardParts.value[editingIndex.value]['chartOptions'] = chartOptions;
  }
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
    chartOptions: getBlankChartOptions(),
  });
  editData(dashboards.value[selectedDashboard.value].layout.length - 1);
}

const editingModeRaw = ref(false);

watch(editChartOptions, (newValue) => {
  livePreviewChartOptions(newValue);
});

function deleteDashboardPart(index) {
  if (confirm('Are you sure you want to delete this dashboard part?')) {
    resetEditing();
    dashboards.value[selectedDashboard.value].layout.splice(index, 1);
    submitChanges();
  }
}

function addNewDashboard() {
  toast.info('Not implemented yet');
}
function deleteDashboard() {
  requests.deleteDashboard(dashboards.value[selectedDashboard.value].id)
    .then(() => {
      dashboards.value.splice(selectedDashboard.value, 1);
      selectedDashboard.value = -1;
      toast.success('Dashboard deleted', {timeout: 2000});
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });
}


</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card title="Controls">
        <template #header>
          <div class="grid grid-cols-3">
            <DashButton v-if="editMode" class="btn-sm mx-5" text="New" @click="addNewDashboard()"/>
            <DashButton
              v-if="editMode && selectedDashboard !== -1"
              class="btn-sm mx-5 btn-danger dark:btn-danger"
              text="Delete"
              @click="deleteDashboard"/>
            <div v-else></div>
            <div class="pt-1">
              <Switch class="d-inline-block mt-4" v-model="editMode" label="Edit Mode"/>
            </div>
          </div>
        </template>
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
      >
        <template v-if="editingIndex === null || editingIndex === index">
          <div class="col-span-12 2xl:col-span-4" :key="dashboardPart.name">
            <Card :title=dashboardPart.name>
              <template #header v-if="editMode">
                <DashButton v-if="editingIndex === index" class="btn-sm dark:btn-danger mx-3" @click="deleteDashboardPart(index)">
                  <Icon icon="heroicons-outline:trash"/>
                </DashButton>
                <DashButton class="btn-sm mx-3" text="Edit Data" @click="editData(index)"/>
                <DashButton class="btn-sm mx-3" text="Edit Chart" @click="editChart(index)"/>
              </template>
              <div class="grid grid-cols-12 gap-5">
                <div class="col-span-full">
                  <apexchart
                    class="text-slate-700 dark:text-slate-300"
                    :type="dashboardPart.chartOptions.chart.type"
                    :options="dashboardPart.chartOptions"
                    :series="dashboardPart.series"
                    height="auto"
                  />
                </div>
              </div>
            </Card>
          </div>

        </template>
      </template>


      <template v-if="editingIndex !== null && currentlyEditing === 'query'">
        <div class="col-span-12 2xl:col-span-8">
          <Card :title="`Editing Query for ${dashboards[selectedDashboard].layout[editingIndex].query.name}`">
            <template #header>
              <div class="grid grid-cols-3">
                <div class="pt-1">
                  <Switch class="d-inline-block mt-4" v-model="editingModeRaw" label="Raw"/>
                </div>
                <DashButton class="btn-sm mx-5 dark:btn-success" text="Save" @click="saveChanges"/>
                <DashButton class="btn-sm mx-5 dark:btn-danger" text="Close" @click="closeEditor"/>
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
        <div class="col-span-12 2xl:col-span-8">
          <Card :title="`Editing Chart Options for ${dashboards[selectedDashboard].layout[editingIndex].query.name}`">
            <template #header>
              <div class="grid grid-cols-3">
                <div class="pt-1">
                  <Switch class="d-inline-block mt-4" v-model="editingModeRaw" label="Raw"/>
                </div>
                <DashButton class="btn-sm mx-5 dark:btn-success" text="Save" @click="saveChanges"/>
                <DashButton class="btn-sm mx-5 dark:btn-danger" text="Cancel" @click="closeEditor"/>
              </div>
            </template>
            <div class="w-full h-full" v-if="!editingModeRaw">
              <DashboardChartEditor v-model="editChartOptions"
              @update:modelValue="(v) => livePreviewChartOptions(v)"/>
            </div>
            <div
              class="w-full h-full"
              v-if="editingModeRaw">
              <TextArea
                classInput="w-full h-full"
                :modelValue="JSON.stringify(editChartOptions, null, 2)"
                @update:modelValue="(v) => {editChartOptions = JSON.parse(v)}"/>
            </div>
          </Card>
        </div>
      </template>

      <div v-if="editMode && editingIndex === null" class="col-span-12 lg:col-span-4">
        <DashButton
          class="btn-dark h-full w-full flex items-center justify-center"
          @click="addDashboardPart"
        >
          <Icon class="text-[8rem]" icon="heroicons-outline:plus"/>
        </DashButton>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
