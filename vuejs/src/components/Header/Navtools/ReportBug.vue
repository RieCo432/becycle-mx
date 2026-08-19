<template>
  <div class="flex flex-row items-center justify-center cursor-pointer" data-tooltip-target="tooltip"
       @click="reportBug">
    <span
        class="h-[32px] w-[32px] sm:bg-gray-500-f7 bg-slate-50 dark:bg-slate-900 dark:text-white
             text-slate-900 rounded-full text-[20px] flex flex-col items-center justify-center"
    >
      <Icon icon="heroicons-outline:code"/>
    </span>
    <span class="ml-1 text-sm md:block hidden font-medium text-slate-600 dark:text-slate-300">Report A Bug</span>
  </div>
</template>
<script>
import {Icon} from "@iconify/vue";

export default {
  name: "ReportBug",
  components: {Icon},
  methods: {
    reportBug() {
      this.$store.bugReportingStore.openModal({})
    }
  }
}
</script>
<style scoped lang="scss">

</style>