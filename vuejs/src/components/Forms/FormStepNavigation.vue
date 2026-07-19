<script setup>

import Button from '@/components/Button/index.vue';
import {defineProps} from 'vue';
import {VueSpinner} from 'vue3-spinners';

const props = defineProps({
  goBack: {
    type: Function,
    required: true,
  },
  submit: {
    type: Function,
    required: true,
  },
  processingSubmit: {
    type: Boolean,
    required: true,
  },
});

</script>

<template>
  <div
    class="mt-10 flex justify-between"
  >
    <Button
      @click.prevent="goBack"
      :disabled="processingSubmit"
      text="Prev"
      btnClass="btn-dark"
    />
    <Button
      btnClass="btn-dark"
      :disabled="processingSubmit">
      <template v-if="!processingSubmit">
        Next
      </template>
      <template v-else>
        <VueSpinner size="20px" class="text-sky-500"/>
      </template>
      </Button>
  </div>
</template>

<style scoped lang="scss">

</style>