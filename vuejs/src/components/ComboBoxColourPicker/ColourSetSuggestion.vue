<script>
import Tooltip from '@/components/Tooltip/index.vue';

export default {
  name: 'ColourSetSuggestion',
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
};
</script>

<template>
  <div class="grid grid-cols-4 lg:grid-cols-6 2xl:grid-cols-10 gap-2">
    <template v-for="c in suggestion" v-bind:key="c.name">
      <div :class="['col-span-1']">
        <Tooltip placement="top" arrow theme="dark">
          <template #button>
            <span
              class="inline-block w-10 h-10 rounded-full"
              :style="`background-color:${c.hex}`"></span>
          </template>
          <span>{{ c.name }} ({{ c.hex }})</span>
        </Tooltip>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">

</style>
