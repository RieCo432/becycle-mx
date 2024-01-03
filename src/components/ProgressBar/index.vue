<template>
  <div class="relative">
    <span
      class="block text-slate-500 font-medium text-lg tracking-[0.01em] mb-2"
      v-if="title"
      >{{ title }}</span
    >
    <div
      class="w-full rounded-[999px] overflow-hidden bg-opacity-10"
      :class="`${backColor} ${height}`"
      v-if="!$slots.default"
    >
      <Bar
        :barColor="barColor"
        :showValue="showValue"
        :value="value"
        :striped="striped"
        :animate="animate"
      />
    </div>
    <div
      class="w-full rounded-[999px] overflow-hidden bg-opacity-10 flex"
      :class="`${backColor} ${height}`"
      v-if="$slots.default"
    >
      <slot></slot>
    </div>
  </div>
</template>
<script>
import Bar from "./Bar.vue";
export default {
  components: {
    Bar,
  },
  props: {
    title: {
      type: String,
      default: "",
    },
    value: {
      type: Number,
      default: 50,
    },
    height: {
      type: String,
      default: "h-2",
    },
    max: {
      type: Number,
      default: 100,
    },
    barColor: {
      type: String,
      default: "bg-slate-900 dark:bg-slate-900",
    },
    backColor: {
      type: String,
      default: "bg-slate-900 dark:bg-slate-700",
    },
    showValue: {
      type: Boolean,
      default: false,
    },
    striped: {
      type: Boolean,
      default: false,
    },
    animate: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
<style lang="scss"></style>
