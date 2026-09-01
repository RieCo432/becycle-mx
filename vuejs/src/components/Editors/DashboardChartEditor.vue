<script setup>
import {computed, ref} from 'vue';
import TextInput from '@/components/TextInput/index.vue';
import Select from '@/components/Select/index.vue';
import requests from '@/requests';
import {Icon} from '@iconify/vue';
import DashButton from '@/components/Button/index.vue';
import Radio from '@/components/Radio/index.vue';
import VueSelect from '@/components/Select/VueSelect.vue';


const chartOptions = defineModel();

const chartTypeOptions = [
  {
    label: 'Line',
    value: 'line',
  },
  {
    label: 'Bar',
    value: 'bar',
  },
  {
    label: 'Area',
    value: 'area',
  },
];

const fillTypeOptions = [
  {
    label: 'Solid',
    value: 'solid',
  },
  {
    label: 'Gradient',
    value: 'gradient',
  },
];


</script>

<template>
  <div class="w-full grid grid-cols-12 gap-3">
    <div class="col-span-3">
      <Select
        label="Chart Type"
        :options="chartTypeOptions"
        v-model="chartOptions.chart.type"
        />
    </div>
    <div class="col-span-3">
      <Select
        label="Fill Type"
        :options="fillTypeOptions"
        v-model="chartOptions.fill.type"
      />
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>