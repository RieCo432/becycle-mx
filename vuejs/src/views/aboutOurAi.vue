<script>
import {marked} from 'marked';
import DOMPurify from 'dompurify';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';

// #511: the public "About our AI" page. Plain Markdown in the database,
// rendered (and sanitised) here — D-3/D-4/D-5, no login required.
export default {
  name: 'aboutOurAi',
  components: {Card},
  data() {
    return {
      content: null,
      loadError: null,
    };
  },
  computed: {
    renderedContent() {
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
      this.loadError = 'The AI disclosure could not be loaded.';
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card title="About our AI">
        <div v-if="loadError" class="text-sm text-danger-500 dark:text-danger-500">
          {{ loadError }}
        </div>
        <div v-else class="ai-disclosure">
          <div v-if="renderedContent" class="text-slate-700 dark:text-slate-300" v-html="renderedContent"/>
          <p v-else class="text-sm text-slate-500 dark:text-slate-400">
            We will publish our AI disclosure here soon.
          </p>
          <h4 class="ai-disclosure-link text-sm text-slate-500 dark:text-slate-400">
            How we handle your data is covered by our
            <router-link to="/privacy-policy" class="text-blue-500">privacy policy</router-link>.
          </h4>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">
// Tailwind's preflight strips default text styling, so give the rendered
// Markdown back the bits a policy document needs.
.ai-disclosure {
  :deep(h1) {
    @apply text-3xl font-semibold mt-2 mb-4 text-slate-900 dark:text-slate-300;
  }
  :deep(h2) {
    @apply text-xl font-semibold mt-6 mb-3 text-slate-900 dark:text-slate-300;
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
  :deep(a) {
    @apply text-blue-500;
  }
}
.ai-disclosure-link {
  @apply mt-8;
}
</style>
