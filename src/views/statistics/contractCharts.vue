<script>
import requests from '@/requests';
import Card from '@/components/Card';
export default {
  name: 'contractCharts',
  components: {
    Card,
  },
  data() {
    return {
      interval: 28,
      loadingContractsTotal: true,
      loadingContractsActive: true,
      loadingContractsNew: true,
      loadingContractsReturned: true,
      contractsTotalSeries: [],
      contractsActiveSeries: [],
      contractsNewSeries: [],
      contractsReturnedSeries: [],
      stackedAreaChartOptions: {
        chart: {
          type: 'area',
          height: 350,
          stacked: true,
          events: {
            selection: function(chart, e) {
              console.log(new Date(e.xaxis.min));
            },
          },
        },
        theme: {
          mode: 'light',
        },
        dataLabels: {
          enabled: false,
        },
        stroke: {
          curve: 'stepline',
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
        xaxis: {
          type: 'datetime',
        },
        yaxis: {
          labels: {
            style: {
              color: '#ffffff',
              cssClass: 'dark:slate-text-300',
            },
          },
        },
      },
    };
  },
  created() {
    this.fetchTotalContractsTimeSeries();
    this.fetchActiveContractsTimeSeries();
    this.fetchNewContractsTimeSeries();
    this.fetchReturnedContractsTimeSeries();
  },
  methods: {
    fetchTotalContractsTimeSeries() {
      requests.getTotalContractsDateSeries(this.interval, 'contractType').then((response) => {
        this.contractsTotalSeries = response.data;
        this.loadingContractsTotal = false;
      });
    },
    fetchActiveContractsTimeSeries() {
      requests.getActiveContractsDateSeries(this.interval, 0).then((response) => {
        this.contractsActiveSeries = response.data;
        this.loadingContractsActive = false;
      });
    },
    fetchNewContractsTimeSeries() {
      requests.getNewContractsDateSeries(this.interval).then((response) => {
        this.contractsNewSeries = response.data;
        this.loadingContractsNew = false;
      });
    },
    fetchReturnedContractsTimeSeries() {
      requests.getReturnedContractsDateSeries(this.interval).then((response) => {
        this.contractsReturnedSeries = response.data;
        this.loadingContractsReturned = false;
      });
    },

  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-6">
      <Card title="Total Contracts">
        <apexchart class="text-slate-700 dark:text-slate-300" type="area" :options="stackedAreaChartOptions" :series="contractsTotalSeries"></apexchart>
      </Card>
    </div>
    <div class="col-span-6">
      <Card title="Active Contracts">
        <apexchart class="text-slate-700 dark:text-slate-300" type="area" :options="stackedAreaChartOptions" :series="contractsActiveSeries"></apexchart>
      </Card>
    </div>
    <div class="col-span-6">
      <Card title="New Contracts">
        <apexchart class="text-slate-700 dark:text-slate-300" type="area" :options="stackedAreaChartOptions" :series="contractsNewSeries"></apexchart>
      </Card>
    </div>
    <div class="col-span-6">
      <Card title="Returned Contracts">
        <apexchart class="text-slate-700 dark:text-slate-300" type="area" :options="stackedAreaChartOptions" :series="contractsReturnedSeries"></apexchart>
      </Card>
    </div>
  </div>

</template>

<style lang="scss">
</style>
