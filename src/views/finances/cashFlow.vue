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
      interval: 63,
      gracePeriod: 184,
      startDate: null,
      endDate: null,
      areaChartOptionsDateSeries: {
        chart: {
          type: 'area',
          height: 300,
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
              colors: ['#dddddd'],
            },
            formatter: (val) => (`\u00A3${val}`),
          },
          axisTicks: {
            color: '#dddddd',
          },
          title: {
            text: 'Value of Deposits',
            style: {
              color: '#dddddd',
            },
          },
        },
      },
      cashflowAreaChartOptionsDateSeries: {
        chart: {
          type: 'area',
          height: 300,
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
              colors: ['#dddddd'],
            },
            formatter: (val) => (`\u00A3${val}`),
          },
          axisTicks: {
            color: '#dddddd',
          },
          title: {
            text: 'Cashflow',
            style: {
              color: '#dddddd',
            },
          },
        },
      },
      depositReturnPercentageMixedChart: {
        chart: {
          type: 'line',
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
          type: 'solid',
        },
        markers: {
          size: [6, 0],
        },
        legend: {
          position: 'top',
          horizontalAlign: 'left',
          labels: {
            colors: ['#dddddd'],
          },
        },
        tooltip: {
          theme: 'dark',
          shared: false,
          intersect: true,
        },
        xaxis: {
          show: true,
          type: 'numeric',
          labels: {
            style: {
              colors: '#dddddd',
            },
          },
          axisTicks: {
            colors: ['#dddddd'],
          },
        },
        yaxis: {
          show: true,
          min: 0,
          max: 100,
          labels: {
            style: {
              colors: ['#dddddd'],
            },
            formatter: (val) => (`${val}%`),
          },
          axisTicks: {
            colors: ['#dddddd'],
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
            colors: ['#CBD5E1'],
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
                  colors: ['#dddddd'],
                  formatter: (s) => (s.replaceAll('_', ' ')),
                },
                value: {
                  show: true,
                  fontSize: '16px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#dddddd',
                  formatter: (s) => (s.replace('', '\u00A3')),
                },
                total: {
                  show: true,
                  fontSize: '20px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#dddddd',
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
            colors: ['#CBD5E1'],
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
                  colors: ['#dddddd'],
                  formatter: (s) => (s.replaceAll('_', ' ')),
                },
                value: {
                  show: true,
                  fontSize: '16px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#dddddd',
                  formatter: (s) => (s.replace('', '\u00A3')),
                },
                total: {
                  show: true,
                  fontSize: '20px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#dddddd',
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
            colors: ['#CBD5E1'],
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
                  colors: ['#dddddd'],
                  formatter: (s) => (s.replaceAll('_', ' ')),
                },
                value: {
                  show: true,
                  fontSize: '16px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#dddddd',
                  formatter: (s) => (s.replace('', '\u00A3')),
                },
                total: {
                  show: true,
                  fontSize: '20px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter',
                  color: '#dddddd',
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
      requests.getPercentageDepositReturnedAfterMonths(this.interval, this.startDate, this.endDate).then((response) => {
        this.percentageDepositReturnedAfterMonthsSeries = response.data;
      });
    },
    fetchWorstCaseRequiredDepositFloatSeries() {
      requests.getWorstCaseRequiredDepositFloat(this.interval).then((response) => {
        this.worstCaseRequiredDepositFloatChartOptions.labels.splice(0, this.worstCaseRequiredDepositFloatChartOptions.labels.length, ...Object.keys(response.data));
        this.worstCaseRequiredDepositFloatSeries = Object.values(response.data);
      });
    },
    fetchRealisticRequiredDepositFloatSeries() {
      requests.getRealisticRequiredDepositFloat(this.interval, this.gracePeriod).then((response) => {
        this.realisticRequiredDepositFloatChartOptions.labels.splice(0, this.realisticRequiredDepositFloatChartOptions.labels.length, ...Object.keys(response.data));
        this.realisticRequiredDepositFloatSeries = Object.values(response.data);
      });
    },
    fetchActualCashflowSeries() {
      requests.getActualCashflow(this.interval, this.startDate, this.endDate).then((response) => {
        this.actualCashflowSeries = response.data;
        this.updateStartDate(this.actualCashflowSeries[0].data[0][0]);
        this.updateEndDate(this.actualCashflowSeries[0].data[this.actualCashflowSeries[0].data.length -1][0]);
      });
    },
    fetchProvisionalCashflowSeries() {
      requests.getProvisionalCashflow(this.interval, this.startDate, this.endDate).then((response) => {
        this.provisionalCashflowSeries = response.data;
        this.updateStartDate(this.provisionalCashflowSeries[0].data[0][0]);
        this.updateEndDate(this.provisionalCashflowSeries[0].data[this.provisionalCashflowSeries[0].data.length -1][0]);
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
    },
    fetchGracePeriodDependants() {
      this.fetchDepositsStatus();
      this.fetchRealisticRequiredDepositFloatSeries();
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
                :max="371"
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
    <div class="col-span-4">
      <Card title="Deposit Flow">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area" :options="areaChartOptionsDateSeries" :series="depositFlowSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-4">
      <Card title="Deposits Status">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="donut" :options="depositsStatusChartOptions" :series="depositsStatusSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-4">
      <Card title="Average Percentage of deposit returned">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="line" :options="depositReturnPercentageMixedChart" :series="percentageDepositReturnedAfterMonthsSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-4">
      <Card title="Estimate: Everyone returns today">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="donut" :options="worstCaseRequiredDepositFloatChartOptions" :series="worstCaseRequiredDepositFloatSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-4">
      <Card title="Estimate: Everyone returns normally">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="donut" :options="realisticRequiredDepositFloatChartOptions" :series="realisticRequiredDepositFloatSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-4">
      <Card title="Actual Expenses and Income">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area" :options="cashflowAreaChartOptionsDateSeries" :series="actualCashflowSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-4">
      <Card title="Provisional Expenses and Income">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-full">
            <apexchart @zoomed="handleSelection" class="text-slate-700 dark:text-slate-300" type="area" :options="cashflowAreaChartOptionsDateSeries" :series="provisionalCashflowSeries"></apexchart>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
