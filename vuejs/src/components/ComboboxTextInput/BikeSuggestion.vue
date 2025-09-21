<template>
  <div :class="['flex items-center justify-between', active ? 'font-semibold' : '']">
    <span>{{ makeBikeLegible(suggestion) }}</span>
    <template v-for="c in suggestion.colours" v-bind:key="c.name">
      <Tooltip placement="top" arrow theme="dark">
        <template #button>
          <span
              class="inline-block w-10 h-10 rounded-full"
              :style="`background-color:${c.hex}`"
          ></span>
        </template>
        <span>{{ c.name }} ({{ c.hex }})</span>
      </Tooltip>
    </template>
  </div>
</template>

<script>
import Tooltip from '@/components/Tooltip/index.vue';

export default {
  name: 'BikeSuggestion',
  components: {
    Tooltip
  },
  props: {
    suggestion: {
      type: Object,
      required: true
    },
    active: {
      type: Boolean,
      required: true
    },
    makeBikeLegible: {
      type: Function,
      required: true
    }
  }
};
</script>

<style scoped lang="scss">
</style>