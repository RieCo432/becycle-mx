<script>
import UpdateLlmSettingsCard from '@/components/Card/UpdateLlmSettingsCard.vue';
import LlmPromptPreviewCard from '@/components/Card/LlmPromptPreviewCard.vue';
import UpdateChatIntentsCard from '@/components/Card/UpdateChatIntentsCard.vue';
import UpdateAiDisclosureCard from '@/components/Card/UpdateAiDisclosureCard.vue';

export default {
  name: 'llmSettings',
  components: {UpdateLlmSettingsCard, LlmPromptPreviewCard, UpdateChatIntentsCard, UpdateAiDisclosureCard},
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12 xl:col-span-6">
      <UpdateLlmSettingsCard></UpdateLlmSettingsCard>
    </div>
    <div class="col-span-12 xl:col-span-6">
      <LlmPromptPreviewCard></LlmPromptPreviewCard>
    </div>
    <div class="col-span-12">
      <UpdateChatIntentsCard></UpdateChatIntentsCard>
    </div>
    <div class="col-span-12 xl:col-span-6">
      <UpdateAiDisclosureCard></UpdateAiDisclosureCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
