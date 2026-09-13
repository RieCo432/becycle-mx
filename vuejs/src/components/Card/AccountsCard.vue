<script setup>
import {defineProps, ref, watch} from 'vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import dateUtils from '@/util/dateUtils';
import moneyUtils from '@/util/moneyUtils';
import {useThemeSettingsStore} from '@/store/themeSettings';
import {useToast} from 'vue-toastification';
import {Icon} from '@iconify/vue';

const themeSettingsStore = useThemeSettingsStore();
const toast = useToast();

const props = defineProps({
  accounts: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
});

const accountsData = ref({});
const loadingAccountsData = ref(true);

const accountColours = {
  default: {
    class: 'text-sky-500',
    colour: '#0ff',
  },
  asset: {
    class: 'text-green-500',
    colour: '#00ff00',
  },
  liability: {
    class: 'text-red-500',
    colour: '#ff0000',
  },
  expense: {
    class: 'text-orange-500',
    colour: '#ff8000',
  },
  revenue: {
    class: 'text-yellow-500',
    colour: '#ffff00',
  },
  equity: {
    class: 'text-purple-500',
    colour: '#ff00ff',
  },
};

function getChartOptions(account) {
  return {
    chart: {
      toolbar: {
        autoSelected: 'pan',
        show: false,
      },
      offsetX: 0,
      offsetY: 0,
      zoom: {
        enabled: false,
      },
      sparkline: {
        enabled: true,
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: 'smooth',
      width: 2,
    },
    colors: [accountColours[account.type].colour],
    tooltip: {
      theme: themeSettingsStore.theme,
    },
    grid: {
      show: false,
      padding: {
        left: 0,
        right: 0,
      },
    },
    yaxis: {
      show: false,
      labels: {
        formatter: moneyUtils.moneyFormatter,
      },
    },
    fill: {
      type: 'solid',
      opacity: [0.1],
    },
    legend: {
      show: false,
    },
    xaxis: {
      type: 'datetime',
      offsetX: 0,
      offsetY: 0,
      show: false,
      labels: {
        offsetX: 0,
        show: false,
      },
      axisBorder: {
        offsetX: 0,
        show: false,
      },
    },
  };
}

function getQuery(accountId) {
  const account = props.accounts.find((account) => account.id === accountId);
  return {
    name: account.id,
    series: [{name: account.name, query: [account.id]}],
    startDate: '#startdate#',
    endDate: '#enddate#',
    interval: 'monhtly',
    mode: 'period',
    dimension: 'balance',
    fundId: null,
  };
}

function getAccountsData() {
  const {start: startDate, end: endDate} = dateUtils.getPastSixMonths();
  const allQueries = props.accounts.map((account) => getQuery(account.id));

  const queryString = JSON.stringify(allQueries)
    .replaceAll('#startdate#', dateUtils.convertDateToPickerString(startDate))
    .replaceAll('#enddate#', dateUtils.convertDateToPickerString(endDate));

  const dashboardQuery = {
    name: 'My Dashboard',
    queries: JSON.parse(queryString),
  };
  
  requests.getDashboard(dashboardQuery)
    .then((response) => {
      const parts = response.data.parts;
      accountsData.value = {};
      for (const part of parts) {
        accountsData.value[part.name] = part.series.map(
          (seriesData) => {
            return {
              name: `${seriesData.name}${seriesData.meta?.flow? `_${seriesData.meta.flow}` : ''}`,
              data: seriesData.data.map(
                (dataPoint) => (
                  {
                    x: new Date(dataPoint.date).getTime(),
                    y: dataPoint.value,
                  }
                ),
              ).toSorted((a, b) => Date.parse(a.x) - Date.parse(b.x)),
            };
          },
        );
      }
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    })
    .finally(() => {
      loadingAccountsData.value = false;
    });
}

watch(() => props.loading, (newValue) => {
  console.log('loading changed', newValue);
  if (!newValue) {
    getAccountsData();
  }
});

</script>

<template>
  <Card :title="title">
    <div v-if="!loading && !loadingAccountsData" class="grid grid-cols-2 gap-5">
      <template v-for="account in accounts.toSorted((a, b) => a.name.localeCompare(b.name))" :key="account.id">
        <div class="col-span-1 grid grid-cols-7 bg-slate-200 dark:bg-slate-900 p-2 rounded-lg gap-2">
          <div class="col-span-1 p-3">
            <Icon :class="`w-full h-full aspect-square self-center ${accountColours[account.type].class} dark:${accountColours[account.type].class}`" icon="heroicons-outline:banknotes" />
          </div>
          <div class="col-span-2 items-center">
            <apexchart
              class="h-full"
              type="area"
              height="65px"
              width="100%"
              :options="getChartOptions(account)"
              :series="accountsData[account.id]"
            />
          </div>
          <div class="col-span-4 grid grid-cols-1 content-between">
            <span class="text-slate-600 dark:text-slate-300 text-sm mb-1 font-medium text-start align-text-top">
                {{ account.name }}
              </span>
            <span class="text-slate-900 dark:text-white text-lg font-medium text-start align-text-bottom">
                {{ moneyUtils.moneyFormatter(account.balance) }}
              </span>
<!--            <div class="flex space-x-3">-->
<!--              <div class="flex-1">-->
<!--                -->
<!--              </div>-->
<!--            </div>-->
          </div>
          
          
        </div>
      </template>
    </div>
  </Card>

</template>

<style scoped lang="scss">

</style>
