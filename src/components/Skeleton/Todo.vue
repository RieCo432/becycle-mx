<template>
  <div class="divide-y divide-slate-100 dark:divide-slate-700">
    <div class="p-4 w-full mx-auto" v-for="(item, i) in items" :key="i">
      <div class="animate-pulse flex items-center space-x-4">
        <div class="flex-none flex space-x-2 items-center">
          <div class="rounded h-5 w-5 bg-[#C4C4C4] dark:bg-slate-500"></div>
          <div class="rounded h-5 w-5 bg-[#C4C4C4] dark:bg-slate-500"></div>
          <div
            class="h-8 w-8 rounded-full bg-[#C4C4C4] dark:bg-slate-500"
          ></div>
        </div>
        <div class="flex-1 bg-[#C4C4C4] dark:bg-slate-500 h-2"></div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    count: {
      type: Number,
      default: 6,
    },
  },

  computed: {
    items() {
      return Array.from({ length: this.count });
    },
  },
};
</script>
<style lang=""></style>
