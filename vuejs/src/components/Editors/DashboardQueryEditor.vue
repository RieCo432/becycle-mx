<script setup>
import {computed, ref} from 'vue';
import TextInput from '@/components/TextInput/index.vue';
import Select from '@/components/Select/index.vue';
import requests from '@/requests';
import {Icon} from '@iconify/vue';
import DashButton from '@/components/Button/index.vue';
import Radio from '@/components/Radio/index.vue';
import VueSelect from '@/components/Select/VueSelect.vue';


const graphQuery = defineModel();
const dimensionOptions = [
  {
    label: 'Cash Flow',
    value: 'cashflow',
  },
  {
    label: 'Balance',
    value: 'balance',
  },
];
const fundOptions = ref([
  {
    label: 'All',
    value: 'null',
  },
]);

const modeOptions = [
  {
    label: 'Moment',
    value: 'moment',
  },
  {
    label: 'Period',
    value: 'period',
  },
];

requests.getFunds()
  .then((response) => {
    fundOptions.value.push(
      ...response.data.map((fund) => ({
        label: fund.name,
        value: fund.id,
      })),
    );
  })
  .catch((error) => {
    toast.error(error.response.data.detail.description, {timeout: 2000});
  });


const fundId = computed({
  get: () => graphQuery.value.fundId ?? 'null',
  set: (value) => {
    graphQuery.value.fundId = value === 'null' ? null : value;
  },
});


const queryModeOptions = [
  {
    label: 'Type',
    value: 'type',
  },
  {
    label: 'List',
    value: 'list',
  },
];

const queryModeTypeOptions = [
  {
    label: 'Dividend',
    value: 'dividend',
  },
  {
    label: 'Expense',
    value: 'expense',
  },
  {
    label: 'Asset',
    value: 'asset',
  },
  {
    label: 'Liability',
    value: 'liability',
  },
  {
    label: 'Equity',
    value: 'equity',
  },
  {
    label: 'Revenue',
    value: 'revenue',
  },
];


const accountsSortingFunction = (a, b) => {
  if (a.type !== b.type) {
    return (
      queryModeTypeOptions.findIndex((option) => option.value === a.type) -
      queryModeTypeOptions.findIndex((option) => option.value === b.type)
    );
  }
  return a.name.localeCompare(b.name);
};


const queryModeListOptions = ref([]);
requests.getAccounts().then((response) => {
  queryModeListOptions.value = response.data.toSorted(accountsSortingFunction).map((account) => ({
    label: account.name,
    value: account.id,
  }));
  queryModeListOptions.value.push('cat');
});

const queryModes = computed({
  get: () => graphQuery.value.series.map((series) => typeof series.query === 'string' ? 'type' : 'list'),
});

function setQueryMode(i, value) {
  graphQuery.value.series[i].query = value === 'list' ? [] : '';
}

const queryModeList = computed({
  get: () => graphQuery.value.series.map((series) => typeof series.query === 'string' ? [] : series.query.map((accountId) => ({
    label: queryModeListOptions.value.find((option) => option.value === accountId)?.label,
    value: accountId,
  }))),
});

function setQueryModeList(i, value) {
  console.log(value);
  graphQuery.value.series[i].query = value.map((item) => item.value);
}

function changeQueryMode(evt) {
  if (evt.target.value === 'moment') {
    delete graphQuery.value['startDate'];
    delete graphQuery.value['endDate'];
    graphQuery.value['moment'] = '#enddate#';
  } else if (evt.target.value === 'period') {
    delete graphQuery.value['moment'];
    graphQuery.value['startDate'] = '#startdate#';
    graphQuery.value['endDate'] = '#enddate#';
  }
}

function moveSeriesDown(index) {
  const temp = graphQuery.value.series[index];
  graphQuery.value.series[index] = graphQuery.value.series[index + 1];
  graphQuery.value.series[index + 1] = temp;
}

function moveSeriesUp(index) {
  const temp = graphQuery.value.series[index];
  graphQuery.value.series[index] = graphQuery.value.series[index - 1];
  graphQuery.value.series[index - 1] = temp;
}

const cashflowOptions = [
  {
    label: 'credit',
    value: 'credit',
  },
  {
    label: 'debit',
    value: 'debit',
  },
  {
    label: 'net',
    value: 'net',
  },
];

const cashflowDirectionsList = computed({
  get: () => graphQuery.value.series.map((series) => {
    console.log(series);
    return cashflowOptions.filter((option) => series[option.value]);
  }),
});

function setCashflowDirectionsList(index, valueRaw) {
  console.log(valueRaw);
  const value = valueRaw.map((item) => item.value);
  console.log(value);
  if (!value.includes('credit')) {
    delete graphQuery.value.series[index].credit;
  } else {
    graphQuery.value.series[index].credit = true;
  }
  if (!value.includes('debit')) {
    delete graphQuery.value.series[index].debit;
  } else {
    graphQuery.value.series[index].debit = true;
  }
  if (!value.includes('net')) {
    delete graphQuery.value.series[index].net;
  } else {
    graphQuery.value.series[index].net = true;
  }
}

</script>

<template>
  <div class="w-full grid grid-cols-12 gap-3">
    <div class="col-span-3">
      <TextInput
        label="Graph Name"
        v-model="graphQuery.name"/>
    </div>
    <div class="col-span-3">
      <Select
        label="Dimension"
        v-model="graphQuery.dimension"
        :options="dimensionOptions"/>
    </div>
    <div class="col-span-3">
      <Select
        label="Mode"
        v-model="graphQuery.mode"
        :options="modeOptions"
        @change="changeQueryMode"
      />
    </div>
    <div class="col-span-3">
      <Select
        label="Fund"
        v-model="fundId"
        :options="fundOptions"/>
    </div>
    <div class="col-span-full">
      <h5 class="text-base text-bold">Series</h5>
    </div>
    <template v-for="(series, i) in graphQuery.series" :key="i">
      <div class="col-span-full grid grid-cols-12 gap-2">
        <div class="col-span-3">
          <TextInput
            label="Name"
            v-model="series.name"/>
        </div>
        <div class="col-span-2">
          <label class="input-label">Accounts By</label>
          <Radio
            v-for="(selector, j) in queryModeOptions"
            :key="j"
            name="querySelector"
            class="mb-5"
            :modelValue="queryModes[i]"
            @update:modelValue="(v) => setQueryMode(i, v)"
            :value="selector.value"
            :label="selector.label"
          />
        </div>
        <div class="col-span-3">
          <template v-if="queryModes[i] === 'list'">
            <VueSelect
              label="Account List"
              :modelValue="queryModeList[i]"
              @update:modelValue="(v) => setQueryModeList(i, v)"
              :options="queryModeListOptions"
              multiple
            />
          </template>
          <template v-else-if="queryModes[i] === 'type'">
            <Select
              label="Account Type"
              v-model="graphQuery.series[i].query"
              :options="queryModeTypeOptions"
            />
          </template>
        </div>
        <div class="col-span-2" v-if="graphQuery.dimension === 'cashflow'">
          <VueSelect
            label="Cashflow Directions"
            :modelValue="cashflowDirectionsList[i]"
            @update:modelValue="(v) => setCashflowDirectionsList(i, v)"
            :options="cashflowOptions"
            multiple
          />
        </div>
        <div class="col-span-2 grid grid-cols-3">
          <div class="col-span-1">
            <DashButton v-if="i < graphQuery.series.length - 1" class="w-full" @click="() => moveSeriesDown(i)">
              <Icon icon="heroicons-outline:arrow-down"/>
            </DashButton>
          </div>
          <div class="col-span-1">
            <DashButton v-if="i > 0" class="w-full" @click="() => moveSeriesUp(i)">
              <Icon icon="heroicons-outline:arrow-up"/>
            </DashButton>
          </div>
          <div class="col-span-1">
            <DashButton class="dark:btn-danger w-full" @click="graphQuery.series.splice(i, 1)">
              <Icon icon="heroicons-outline:trash"/>
            </DashButton>
          </div>
        </div>
      </div>
    </template>
    <div class="col-span-full">
      <DashButton class="w-full" @click="graphQuery.series.push({name: '', query: ''})">
        <Icon icon="heroicons-outline:plus"/>
      </DashButton>
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>
