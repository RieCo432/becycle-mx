<script>
import Card from '@/components/Card/index.vue';
import Textarea from '@/components/Textarea/index.vue';
import Button from '@/components/Button/index.vue';
import requests from '@/requests';
import {onBeforeMount, ref, computed} from 'vue';

export default {
  name: 'LlmPromptPreviewCard',
  components: {
    Card,
    Textarea,
    Button,
  },
  setup() {
    const dynamicBlock = ref('');
    const charCount = ref(0);
    const loaded = ref(false);
    const error = ref('');

    // #505: debugging aid — show the dynamic block exactly as it is assembled
    // from this site's database at call time (the part of the system prompt
    // appended after the persona).
    const refresh = () => {
      loaded.value = false;
      error.value = '';
      requests.getLlmPromptPreview()
        .then((response) => {
          dynamicBlock.value = response.data.dynamicBlock ?? '';
          charCount.value = response.data.charCount ?? dynamicBlock.value.length;
        })
        .catch((err) => {
          error.value = err.response?.data?.detail?.description ?? 'Could not load the prompt preview.';
        })
        .finally(() => {
          loaded.value = true;
        });
    };

    const subtitle = computed(() => {
      if (error.value) return 'Failed to load';
      if (!loaded.value) return 'Loading…';
      return `${charCount.value} characters`;
    });

    const displayValue = computed(() => {
      if (error.value) return error.value;
      if (!loaded.value) return 'Loading…';
      if (dynamicBlock.value) return dynamicBlock.value;
      return '(No dynamic sections — this site\'s database produced nothing for the block.)';
    });

    onBeforeMount(refresh);

    return {dynamicBlock, charCount, loaded, error, refresh, subtitle, displayValue};
  },
};
</script>

<template>
  <Card title="Prompt Preview" :subtitle="subtitle">
    <template #header>
      <Button @click="refresh" text="Refresh" />
    </template>
    <Textarea
      name="llmPromptPreview"
      label="Dynamic block"
      :isReadonly="true"
      :rows="18"
      :modelValue="displayValue"
    />
  </Card>
</template>

<style scoped lang="scss">
</style>
