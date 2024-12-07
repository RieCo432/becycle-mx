<template>
  <Card title="loading..." title-class="animate-pulse" class-name="dark:bg-slate-600">
    <div class="grid lg:grid-cols-6 grid-cols-3 gap-5">
      <div v-for="j in 12" :key="j">
        <div class="mt-3 col-span-1 h-10 w-full rounded bg-[#C4C4C4] dark:bg-slate-500"></div>
      </div>
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
