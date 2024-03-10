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
      loadingContractsTotal: true,
      loadingContractsActive: true,
      loadingContractsNew: true,
      contractsTotalSeries: [],
      contractsActiveSeries: [],
      contractsNewSeries: [],
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
  },
  methods: {
    fetchTotalContractsTimeSeries() {
      requests.getTotalContractsDateSeries(28, 'contractType').then((response) => {
        this.contractsTotalSeries = response.data;
        this.loadingContractsTotal = false;
      });
    },
    fetchActiveContractsTimeSeries() {
      requests.getActiveContractsDateSeries(28, 0).then((response) => {
        this.contractsActiveSeries = response.data;
        this.loadingContractsActive = false;
      });
    },
    fetchNewContractsTimeSeries() {
      requests.getNewContractsDateSeries(28).then((response) => {
        this.contractsNewSeries = response.data;
        this.loadingContractsNew = false;
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

      </Card>
    </div>
  </div>

</template>

<style lang="scss">
</style>
