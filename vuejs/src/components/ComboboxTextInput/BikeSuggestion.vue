<template>
  <div :class="[active ? 'font-semibold' : '']">
    <div class="grid grid-cols-12 gap-2">
      <div class="col-span-9">
        <span>{{ makeBikeLegible(suggestion) }}</span>
      </div>
      <div v-if="suggestion.colours.length < 3" :class="`col-span-${3-suggestion.colours.length}`"></div>
      <template v-for="c in suggestion.colours" v-bind:key="c.name">
        <div :class="['col-span-1']">
          <Tooltip placement="top" arrow theme="dark">
            <template #button>
          <span
              class="inline-block w-10 h-10 rounded-full"
              :style="`background-color:${c.hex}`"
          ></span>
            </template>
            <span>{{ c.name }} ({{ c.hex }})</span>
          </Tooltip>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import Tooltip from '@/components/Tooltip/index.vue';

export default {
  name: 'BikeSuggestion',
  components: {
    Tooltip,
  },
  props: {
    suggestion: {
      type: Object,
      required: true,
    },
    active: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    makeBikeLegible(bike) {
      return `${bike.make} ${bike.model} ${bike.serialNumber}`;
    },
  },
};
</script>

<style scoped lang="scss">
</style>