<script>
import {marked} from 'marked';
import DOMPurify from 'dompurify';
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';

const toast = useToast();

// #511 D-6: admin edit of the public "About our AI" disclosure. Plain
// Markdown with a live preview; the same renderer the public page uses.
export default {
  name: 'UpdateAiDisclosureCard',
  components: {Card, DashButton},
  data() {
    return {
      content: null,
      draft: null,
      editorActive: false,
    };
  },
  computed: {
    // Read mode only - while editing, the text area replaces the preview.
    previewHtml() {
      if (!this.content) {
        return '';
      }
      return DOMPurify.sanitize(marked.parse(this.content));
    },
  },
  created() {
    requests.getAiDisclosure().then((response) => {
      this.content = response.data.content ?? '';
    }).catch(() => {
      toast.error('The AI disclosure could not be loaded.', {timeout: 2000});
    });
  },
  methods: {
    openEditor() {
      this.draft = this.content ?? '';
      this.editorActive = true;
    },
    cancelEditor() {
      this.editorActive = false;
    },
    save() {
      // #511: the write goes through the regular LLM Settings endpoint.
      // Re-read the full settings object first so the PUT carries every
      // field (the endpoint takes the whole object, not a patch).
      requests.getLlmSettings().then((response) => {
        const settings = response.data;
        settings.aiDisclosure = this.draft;
        return requests.putLlmSettings(settings);
      }).then((response) => {
        this.content = response.data.aiDisclosure ?? '';
        this.editorActive = false;
        toast.success('AI disclosure updated', {timeout: 1000});
      }).catch((error) => {
        toast.error(error.response?.data?.detail?.description ?? 'The AI disclosure could not be saved.', {timeout: 2000});
      });
    },
  },
};
</script>

<template>
  <Card title="About our AI" subtitle="Public disclosure - plain Markdown, rendered on the About-our-AI page.">
    <div v-if="content === null">
      <div class="text-sm text-slate-500 dark:text-slate-400">Loading…</div>
    </div>
    <div v-else>
      <!-- Editing: the text area replaces the preview and fills the card. -->
      <div v-if="editorActive" class="grid grid-cols-12 gap-5">
        <div class="col-span-12">
          <textarea
            v-model="draft"
            spellcheck="false"
            placeholder="Markdown text of the public AI disclosure..."
            class="custom-scrollbar w-full min-h-[420px] rounded border border-slate-300 dark:border-slate-600
                   bg-white dark:bg-slate-900 p-3 font-mono text-xs
                   text-slate-800 dark:text-slate-200"
          />
        </div>
        <div class="col-span-12 grid grid-cols-2 gap-5">
          <DashButton class="w-full" @click="cancelEditor">Cancel</DashButton>
          <DashButton class="w-full" @click="save">Save</DashButton>
        </div>
      </div>
      <!-- Read mode: the rendered preview, with an Edit affordance. -->
      <div v-else>
        <div v-if="previewHtml" class="ai-disclosure-editor text-slate-700 dark:text-slate-300" v-html="previewHtml"/>
        <p v-else class="text-sm text-slate-500 dark:text-slate-400">
          The disclosure is currently empty - the public page will show a placeholder.
        </p>
        <div class="mt-4 text-right">
          <DashButton v-if="$can('putLlmSettings')" class="w-full sm:w-auto" @click="openEditor">Edit</DashButton>
        </div>
      </div>
    </div>
  </Card>
</template>

<style scoped lang="scss">
// Tailwind's preflight strips default text styling, so give the rendered
// Markdown back the bits a policy document needs.
.ai-disclosure-editor {
  :deep(h1) {
    @apply text-3xl font-semibold mt-1 mb-4 text-slate-900 dark:text-slate-300;
  }
  :deep(h2) {
    @apply text-xl font-semibold mt-5 mb-3 text-slate-900 dark:text-slate-300;
  }
  :deep(p) {
    @apply my-3 leading-relaxed;
  }
  :deep(ul) {
    @apply my-3 list-disc pl-6 space-y-1;
  }
  :deep(strong) {
    @apply font-semibold;
  }
}
</style>
