<template>
  <Card title="loading..." title-class="animate-pulse" class-name="dark:bg-slate-600">
      <div class="flex flex-col h-full animate-pulse">
        <div class="flex-1 py-6 space-y-4">
          <div class="h-[6px] bg-[#C4C4C4] dark:bg-slate-500"></div>
          <div class="h-[6px] bg-[#C4C4C4] dark:bg-slate-500"></div>
          <div class="h-[6px] bg-[#C4C4C4] dark:bg-slate-500"></div>
          <div class="h-[6px] bg-[#C4C4C4] dark:bg-slate-500"></div>
        </div>
        <div class="h-10 w-40 rounded bg-[#C4C4C4] dark:bg-slate-500"></div>
      </div>
  </Card>
</template>
<script>

import Card from '@/components/Card/index.vue';

export default {
  name: 'ContractClientCardSkeleton',
  components: {Card},
};
</script>
<style lang=""></style>
