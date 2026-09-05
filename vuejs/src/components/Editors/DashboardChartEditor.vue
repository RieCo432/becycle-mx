<script setup>
import TextInput from '@/components/TextInput/index.vue';
import Select from '@/components/Select/index.vue';
import {Icon} from '@iconify/vue';
import {Vue3ColorPicker} from '@cyhnkckali/vue3-color-picker';
import Tooltip from '@/components/Tooltip/index.vue';
import '@cyhnkckali/vue3-color-picker/dist/style.css';
import Checkbox from '@/components/Checkbox/index.vue';
import {useThemeSettingsStore} from '@/store/themeSettings';

const themeSettingsStore = useThemeSettingsStore();
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

const xAxisTypeOptions = [
  {
    label: 'Category',
    value: 'category',
  },
  {
    label: 'Date & Time',
    value: 'datetime',
  },
];

const strokeCurveOptions = [
  {
    label: 'Smooth',
    value: 'smooth',
  },
  {
    label: 'Straight',
    value: 'straight',
  },
  {
    label: 'Step Line',
    value: 'stepline',
  },
  {
    label: 'Monotone Cubic',
    value: 'monotoneCubic',
  },
];

</script>

<template>
  <div class="w-full grid grid-cols-12 grid-rows-1 gap-3">
    <div class="col-span-1">
      <label class="w-full inline-block input-label">
        Series Colours
      </label>
      <div
        v-for="(colour, index) in chartOptions.colors"
        :key="index" class="w-full"
        @click.right.prevent.stop="chartOptions.colors.splice(index, 1)">
        <Tooltip
          placement="top"
          arrow
          :theme="themeSettingsStore.theme"
          interactive
          @click.right.prevent.stop="chartOptions.colors.splice(index, 1)">
          <template #button>
            <span
              class="inline-block w-10 h-10 rounded-full"
              :style="`background-color:${chartOptions.colors[index]}`"
            ></span>
          </template>
          <Vue3ColorPicker
            v-model="chartOptions.colors[index]"
            :theme="themeSettingsStore.theme"
            mode="solid"
            type="HEX"
            :show-alpha="false"
            :show-list="true"
            :show-input-menu="true"
            :show-picker-mode="true"
          />
        </Tooltip>
      </div>
      <div class="col-span-1">
        <span
          class="w-10 h-10 rounded-full
          flex items-center justify-center
          bg-slate-200 dark:bg-slate-700
          text-slate-700 dark:text-slate-300
          hover:bg-slate-300 dark:hover:bg-slate-600
          cursor-pointer"
          @click="chartOptions.colors.push('#4A412A')"
        >
          <Icon icon="heroicons-outline:plus"/>
        </span>
      </div>
    </div>
    <div class="col-span-3">
      <label class="w-full inline-block input-label">
        Fill
      </label>
      <div class="w-full">
        <Select
          label="Type"
          :options="fillTypeOptions"
          v-model="chartOptions.fill.type"
        />
      </div>
      <template v-if="chartOptions.fill.type === 'gradient'">
        <div class="w-full">
          <TextInput
            label="Opacity From"
            type="number"
            v-model="chartOptions.fill.gradient.opacityFrom"
            :error="
              chartOptions.fill.gradient.opacityFrom < 0 ||
              chartOptions.fill.gradient.opacityFrom > 1
                ? 'Opacity must be between 0 and 1'
                : null"
          />
        </div>
        <div class="w-full">
          <TextInput
            label="Opacity To"
            type="number"
            v-model="chartOptions.fill.gradient.opacityTo"
            :error="
              chartOptions.fill.gradient.opacityTo < 0 ||
              chartOptions.fill.gradient.opacityTo > 1
                ? 'Opacity must be between 0 and 1'
                : null"
          />
        </div>
      </template>
    </div>
    <div class="col-span-3">
      <label class="w-full inline-block input-label">
        Chart
      </label>
      <div class="w-full">
        <Select
          label="Type"
          :options="chartTypeOptions"
          v-model="chartOptions.chart.type"
        />
      </div>
      <div class="w-full" v-if="['area', 'line'].includes(chartOptions.chart.type)">
        <Select
          label="Stroke Curve"
          :options="strokeCurveOptions"
          v-model="chartOptions.stroke.curve"
        />
      </div>
      <div class="w-full">
        <Checkbox
          label="Stacked"
          activeClass="ring-primary-500 bg-primary-500"
          v-model="chartOptions.chart.stacked"
        />
      </div>
      <div class="w-full" v-if="chartOptions.chart.type === 'bar'">
        <Checkbox
          label="Distributed"
          activeClass="ring-primary-500 bg-primary-500"
          v-model="chartOptions.plotOptions.bar.distributed"
        />
      </div>
    </div>
    <div class="col-span-2">
      <label class="w-full inline-block input-label">
        X Axis
      </label>
      <div class="w-full">
        <Select
          label="Type"
          :options="xAxisTypeOptions"
          v-model="chartOptions.xaxis.type"
        />
      </div>
    </div>
    <div class="col-span-2">
      <label class="w-full inline-block input-label">
        Y Axis
      </label>
      <div class="w-full">
        <TextInput
          label="Title"
          v-model="chartOptions.yaxis[0].title.text"
        />
      </div>
    </div>

  </div>

</template>

<style scoped lang="scss">

</style>
