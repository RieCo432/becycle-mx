<script setup>

import Button from '@/components/Button/index.vue';
import {defineProps} from 'vue';

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
      :disabled="processingSubmit"
      text="Next"
    />
    <VueSpinner v-if="processingSubmit" size="20px" class="text-sky-500"/>
  </div>
</template>

<style scoped lang="scss">

</style>