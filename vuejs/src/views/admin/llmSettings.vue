<script>
import UpdateLlmSettingsCard from '@/components/Card/UpdateLlmSettingsCard.vue';

export default {
  name: 'llmSettings',
  components: {UpdateLlmSettingsCard},
};
</script>

<template>
  <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">
    <div class="col-span-6 xl:col-span-12">
      <UpdateLlmSettingsCard></UpdateLlmSettingsCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
