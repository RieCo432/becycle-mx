<script>
import 'vue-slider-component/theme/antd.css';
import Card from '@/components/Card/index.vue';
import VueSlider from 'vue-slider-component';
import 'vue-slider-component/theme/antd.css';
import requests from '@/requests';
import {useThemeSettingsStore} from '@/store/themeSettings';
import Select from '@/components/Select/index.vue';

const themeSettingsStore = useThemeSettingsStore();

export default {
  name: 'depositCharts',
  components: {
    Select,
    Card,
    VueSlider,
  },
  data() {
    return {
      interval: 'monthly',
      gracePeriod: 184,
      startDate: null,
      endDate: null,
      expenseTagFilter: '',
      expenseTags: [{label: 'All', value: ''}],
      areaChartOptionsDateSeries: {
        chart: {
          type: 'area',
          height: 300,
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
      cashflowAreaChartOptionsDateSeries: {
        chart: {
          type: 'area',
          height: 300,
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
            formatter: (val) => (`\u00A3${val}`),
          },
          axisTicks: {
            color: '#CBD5E1',
          },
          title: {
            text: 'Cashflow',
            style: {
              color: '#CBD5E1',
            },
          },
        },
      },
      depositReturnPercentageMixedChart: {
        chart: {
          type: 'line',
        },
        dataLabels: {
          enabled: false,
        },
        stroke: {
          curve: 'straight',
        },
        fill: {
          type: 'solid',
        },
        markers: {
          size: [2, 0],
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
          shared: false,
          intersect: true,
        },
        xaxis: {
          show: true,
          type: 'numeric',
          labels: {
            style: {
              colors: '#CBD5E1',
            },
          },
          axisTicks: {
            colors: '#CBD5E1',
          },
          title: {
            text: 'Days Before/After Contract End',
            style: {
              color: '#CBD5E1',
            },
          },
        },
        yaxis: {
          show: true,
          min: 0,
          max: 100,
          labels: {
            style: {
              colors: '#CBD5E1',
            },
            formatter: (val) => (`${val}%`),
          },
          axisTicks: {
            colors: '#CBD5E1',
          },
        },
        plotOptions: {
          bubble: {
            zScaling: true,
          },
        },
      },
      depositsStatusChartOptions: {
        labels: [],
        colors: ['#4669FA', '#FA916B', '#50C793', '#0CE7FA'],
        dataLabels: {
          enabled: true,
          formatter: function(value, opt) {
            return `\u00A3${opt.w.config.series[opt.seriesIndex]}`;
          },
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
                  formatter: (s) => (s.replace('', '\u00A3')),
                },
                total: {
                  show: true,
                  fontSize: '20px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#CBD5E1',
                  formatter: (w) => {
                    console.log(w);
                    return `\u00A3${w.globals.seriesTotals.reduce((a, b) => {
                      return a+b;
                    })}`;
                  },
                },
              },
            },
          },
        },
      },
      worstCaseRequiredDepositFloatChartOptions: {
        labels: [],
        colors: ['#4669FA', '#FA916B'],
        dataLabels: {
          enabled: true,
          formatter: function(value, opt) {
            return `\u00A3${opt.w.config.series[opt.seriesIndex]}`;
          },
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
                  formatter: (s) => (s.replace('', '\u00A3')),
                },
                total: {
                  show: true,
                  fontSize: '20px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#CBD5E1',
                  formatter: (w) => {
                    console.log(w);
                    return `\u00A3${w.globals.seriesTotals.reduce((a, b) => {
                      return a+b;
                    })}`;
                  },
                },
              },
            },
          },
        },
      },
      realisticRequiredDepositFloatChartOptions: {
        labels: [],
        colors: ['#4669FA', '#FA916B'],
        dataLabels: {
          enabled: true,
          formatter: function(value, opt) {
            return `\u00A3${opt.w.config.series[opt.seriesIndex]}`;
          },
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
                  formatter: (s) => (s.replace('', '\u00A3')),
                },
                total: {
                  show: true,
                  fontSize: '20px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#CBD5E1',
                  formatter: (w) => {
                    console.log(w);
                    return `\u00A3${w.globals.seriesTotals.reduce((a, b) => {
                      return a+b;
                    })}`;
                  },
                },
              },
            },
          },
        },
      },
      depositFlowSeries: [],
      depositsStatusSeries: [],
      percentageDepositReturnedAfterMonthsSeries: [],
      worstCaseRequiredDepositFloatSeries: [],
      realisticRequiredDepositFloatSeries: [],
      actualCashflowSeries: [],
      provisionalCashflowSeries: [],
      totalCashflowSeries: [],
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
    fetchDepositFlow() {
      requests.getDepositFlowDateSeries(this.interval, this.startDate, this.endDate).then((response) => {
        this.depositFlowSeries = response.data;
        this.updateStartDate(this.depositFlowSeries[0].data[0][0]);
        this.updateEndDate(this.depositFlowSeries[0].data[this.depositFlowSeries[0].data.length -1][0]);
      });
    },
    fetchDepositsStatus() {
      requests.getDepositsStatus(this.gracePeriod, this.startDate, this.endDate).then((response) => {
        this.depositsStatusChartOptions.labels.splice(0, this.depositsStatusChartOptions.labels.length, ...Object.keys(response.data));
        this.depositsStatusSeries = Object.values(response.data);
      });
    },
    fetchPercentageDepositReturnedAfterMonths() {
      requests.getPercentageDepositReturnedAfterMonths(this.startDate, this.endDate).then((response) => {
        this.percentageDepositReturnedAfterMonthsSeries = response.data;
      });
    },
    fetchWorstCaseRequiredDepositFloatSeries() {
      requests.getWorstCaseRequiredDepositFloat().then((response) => {
        this.worstCaseRequiredDepositFloatChartOptions.labels
          .splice(0, this.worstCaseRequiredDepositFloatChartOptions.labels.length, ...Object.keys(response.data));
        this.worstCaseRequiredDepositFloatSeries = Object.values(response.data);
      });
    },
    fetchRealisticRequiredDepositFloatSeries() {
      requests.getRealisticRequiredDepositFloat(this.gracePeriod).then((response) => {
        this.realisticRequiredDepositFloatChartOptions.labels
          .splice(0, this.realisticRequiredDepositFloatChartOptions.labels.length, ...Object.keys(response.data));
        this.realisticRequiredDepositFloatSeries = Object.values(response.data);
      });
    },
    fetchActualCashflowSeries() {
      requests.getActualCashflow(this.interval, this.startDate, this.endDate,
        this.expenseTagFilter !== '' ? this.expenseTagFilter : null).then((response) => {
        this.actualCashflowSeries = response.data;
        this.updateStartDate(this.actualCashflowSeries[0].data[0][0]);
        this.updateEndDate(this.actualCashflowSeries[0].data[this.actualCashflowSeries[0].data.length -1][0]);
      });
    },
    fetchProvisionalCashflowSeries() {
      requests.getProvisionalCashflow(this.interval, this.startDate, this.endDate,
        this.expenseTagFilter !== '' ? this.expenseTagFilter : null).then((response) => {
        this.provisionalCashflowSeries = response.data;
        this.updateStartDate(this.provisionalCashflowSeries[0].data[0][0]);
        this.updateEndDate(this.provisionalCashflowSeries[0].data[this.provisionalCashflowSeries[0].data.length -1][0]);
      });
    },
    fetchTotalCashflowSeries() {
      requests.getTotalCashflow(this.interval, this.startDate, this.endDate,
        this.expenseTagFilter !== '' ? this.expenseTagFilter : null).then((response) => {
        this.totalCashflowSeries = response.data;
        this.updateStartDate(this.totalCashflowSeries[0].data[0][0]);
        this.updateEndDate(this.totalCashflowSeries[0].data[this.totalCashflowSeries[0].data.length -1][0]);
      });
    },
    fetchAllSeries() {
      this.fetchDepositFlow();
      this.fetchDepositsStatus();
      this.fetchPercentageDepositReturnedAfterMonths();
      this.fetchWorstCaseRequiredDepositFloatSeries();
      this.fetchRealisticRequiredDepositFloatSeries();
      this.fetchActualCashflowSeries();
      this.fetchProvisionalCashflowSeries();
      this.fetchTotalCashflowSeries();
    },
    fetchGracePeriodDependants() {
      this.fetchDepositsStatus();
      this.fetchRealisticRequiredDepositFloatSeries();
    },
    handleSelection(chart, {xaxis, yaxis}) {
      if (xaxis.min) {
        const newStartDate = new Date(xaxis.min);
        this.startDate = `${newStartDate.getUTCFullYear()}-${(newStartDate.getUTCMonth() + 1).toString()
          .padStart(2, '0')}-${newStartDate.getUTCDate().toString().padStart(2, '0')}`;
      } else {
        this.startDate = null;
      }
      if (xaxis.max) {
        const newEndDate = new Date(xaxis.max);
        this.endDate = `${newEndDate.getUTCFullYear()}-${(newEndDate.getUTCMonth() + 1).toString()
          .padStart(2, '0')}-${newEndDate.getUTCDate().toString().padStart(2, '0')}`;
      } else {
        this.endDate = null;
      }
      this.fetchAllSeries();
    },
    getExpenseTags() {
      requests.getExpenseTags().then((response) => {
        this.expenseTags.splice(0, this.expenseTags.length, {
          label: 'All',
          value: '',
        });
        this.expenseTags.push(...response.data.map((t) => (
          {
            label: `${t.id} --- ${t.description}`,
            value: t.id,
          }
        )));
      });
      this.expenseTagFilter = '';
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
    this.getExpenseTags();
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
                :max="371"
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
                @drag-end="fetchGracePeriodDependants"
            ></vue-slider>
          </div>
          <div class="col-span-12 lg:col-span-4 content-center">
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
          <div class="col-span-12 lg:col-span-4 content-center">
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
          <div class="col-span-12 lg:col-span-4 content-center">
            <label class="text-slate-700 dark:text-slate-300">Filter By Tag</label>
            <Select
                :options="expenseTags"
                v-model="expenseTagFilter"
                disable-placeholder
                @input="fetchAllSeries"
            ></Select>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-6">
      <Card title="Actual Cashflow">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area"
                       :options="cashflowAreaChartOptionsDateSeries" :series="actualCashflowSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-6">
      <Card title="Provisional Cashflow">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area"
                       :options="cashflowAreaChartOptionsDateSeries" :series="provisionalCashflowSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-6">
      <Card title="Total Expenses and Income">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area"
                       :options="cashflowAreaChartOptionsDateSeries" :series="totalCashflowSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-6">
      <Card title="Deposit Flow">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area"
                       :options="areaChartOptionsDateSeries" :series="depositFlowSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-4">
      <Card title="Estimate: Everyone returns today">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="donut"
                       :options="worstCaseRequiredDepositFloatChartOptions" :series="worstCaseRequiredDepositFloatSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-4">
      <Card title="Estimate: Everyone returns normally">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="donut"
                       :options="realisticRequiredDepositFloatChartOptions" :series="realisticRequiredDepositFloatSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-4">
      <Card title="Deposits Status">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="donut"
                       :options="depositsStatusChartOptions" :series="depositsStatusSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-12 lg:col-span-8">
      <Card title="Average Percentage of deposit returned">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="line"
                       :options="depositReturnPercentageMixedChart" :series="percentageDepositReturnedAfterMonthsSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
