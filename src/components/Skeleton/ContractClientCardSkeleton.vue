<template>
  <div class="flex flex-col h-full animate-pulse">
    <div class="flex-1" >
      <div class="py-6 space-y-4">
        <div class="h-[6px] bg-[#C4C4C4] dark:bg-slate-500"></div>
        <div class="h-[6px] bg-[#C4C4C4] dark:bg-slate-500"></div>
      </div>
    </div>
    <div class="h-10 w-40 rounded bg-[#C4C4C4] dark:bg-slate-500"></div>
  </div>
</template>
<script>
import DashButton from '@/components/Button/index.vue';

export default {
  name: 'ContractClientCardSkeleton',
  components: {DashButton},
};
</script>
<style lang=""></style>
