<template>
  <div class="divide-y divide-slate-100 dark:divide-slate-700">
    <div class="grid grid-cols-12 gap-5 h-full animate-pulse items-center">
      <div  class="col-span-1" v-for="(item, i) in items" :key="i">
        <div class="h-full grid grid-cols-1 gap-y-4" :key="i">
          <div class="col-span-1 h-64">
            <div class="flex-1 w-3 bg-[#C4C4C4] dark:bg-slate-500 h-full mx-auto"></div>
          </div>
          <div class="col-span-1 h-8">
            <div class="rounded h-full w-full bg-[#C4C4C4] dark:bg-slate-500"></div>
          </div>
          <div class="col-span-1 h-8">
            <div class="rounded h-full w-full bg-[#C4C4C4] dark:bg-slate-500"></div>
          </div>
        </div>
      </div>
      <div  class="col-span-1 col-end-13">
        <div class="h-full grid grid-cols-1 gap-y-4">
          <div class="col-span-1 h-64">
            <div class="flex-1 w-3 bg-[#C4C4C4] dark:bg-slate-500 h-full mx-auto"></div>
          </div>
          <div class="col-span-1 h-8">
            <div class="rounded h-full w-full bg-[#C4C4C4] dark:bg-slate-500"></div>
          </div>
          <div class="col-span-1 h-8">
            <div class="rounded h-full w-full bg-[#C4C4C4] dark:bg-slate-500"></div>
          </div>
        </div>
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
      return Array.from({length: this.count});
    },
  },
};
</script>
<style lang=""></style>
