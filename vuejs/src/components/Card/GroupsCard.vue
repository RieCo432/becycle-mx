<script setup>
import {defineProps} from 'vue';
import Card from '@/components/Card/index.vue';


const props = defineProps({
  groups: {
    type: Array,
    required: false,
  },
  loading: {
    type: Boolean,
    required: false,
  },
});
</script>

<template>
  <Card
    title="Groups"
    class-name="rounded-3xl"
  >
    <div class="grid grid-cols-12 gap-5">
      <template v-if="!loading">
        <template
          v-for="group in groups"
          :key="group.id"
        >
          <div class="col-span-full">
            <span class="text-slate-900 dark:text-white text-lg font-medium">
              {{ group.name }}
            </span>
          </div>
        </template>
      </template>
      <template v-else>
        <div
          v-for="i in 3"
          :key="i"
          class="col-span-full h-[74px] bg-[#C4C4C4] dark:bg-slate-500 animate-pulse rounded-lg"/>
      </template>
    </div>
  </Card>

</template>

<style scoped lang="scss">

</style>