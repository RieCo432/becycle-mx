<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import dateUtils from '@/util/dateUtils';

export default {
  name: 'aiReplies',
  components: {Card},
  data() {
    return {
      loading: true,
      entries: [],
      loadError: null,
    };
  },
  created() {
    this.load();
  },
  methods: {
    load() {
      this.loading = true;
      requests.getAiReplies().then((response) => {
        this.entries = response.data;
        this.loadError = null;
      }).catch((error) => {
        // 403 (not an admin) already toasts globally via validateStatus —
        // this is the in-page state for that and any other failure.
        this.loadError = error.response?.data?.detail?.description ?? 'AI replies could not be loaded.';
      }).finally(() => {
        this.loading = false;
      });
    },
    time(dateString) {
      return dateUtils.convertToConvenientString(dateString);
    },
    // #510 A-3: the intent slug or FAQ key as recorded, or the free-form
    // "none" fallback; null would be a non-classified route (not expected on
    // client-route replies, but shown rather than crashing).
    intentLabel(entry) {
      if (!entry.intent || entry.intent === 'none') {
        return 'free-form';
      }
      return entry.intent;
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5 h-full min-h-0">
    <div class="col-span-12 min-h-0">
      <Card
        title="AI Replies — Client Conversations"
        className="h-full min-h-0"
        bodyClass="p-6 flex flex-col h-full min-h-0 overflow-hidden"
      >
        <p class="text-sm text-slate-500 dark:text-slate-400 flex-none -mt-2 mb-4">
          Every reply the workshop assistant sent in a client conversation, newest first — with the
          detected intent and the client messages that prompted it (the most recent ones before each reply).
        </p>

        <div class="custom-scrollbar flex-1 min-h-0 overflow-y-auto">
          <div
            v-if="loading"
            class="py-8 text-center text-sm text-slate-500 dark:text-slate-400"
          >
            Loading…
          </div>

          <div v-else-if="loadError" class="py-8 text-center text-sm text-danger-500 dark:text-danger-500">
            {{ loadError }}
          </div>

          <div
            v-else-if="entries.length === 0"
            class="py-8 text-center text-sm text-slate-500 dark:text-slate-400"
          >
            No AI replies in client conversations yet.
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="entry in entries"
              :key="entry.id"
              class="border border-slate-100 dark:border-slate-700 rounded-md p-4"
            >
              <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
                <span class="font-semibold text-slate-800 dark:text-slate-200">
                  {{ entry.client.firstName }} {{ entry.client.lastName }}
                </span>
                <span class="text-slate-400">{{ time(entry.sentOn) }}</span>
                <span
                  class="inline-block align-middle rounded bg-slate-200 dark:bg-slate-700
                         px-1.5 py-0.5 text-[10px] font-semibold leading-none
                         text-slate-500 dark:text-slate-300"
                  :title="`Detected intent: ${entry.intent ?? '—'}`"
                >{{ intentLabel(entry) }}</span>
              </div>

              <p
                class="mt-2 text-sm text-slate-700 dark:text-slate-300
                       whitespace-pre-wrap break-words"
              >
                {{ entry.body }}
              </p>

              <div class="mt-3 border-t border-slate-100 dark:border-slate-700 pt-3">
                <div class="text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
                  Prompted by ({{ entry.context.length }} client message{{ entry.context.length === 1 ? '' : 's' }})
                </div>
                <ul v-if="entry.context.length > 0" class="mt-2 space-y-1">
                  <li
                    v-for="message in entry.context"
                    :key="message.id"
                    class="text-sm text-slate-600 dark:text-slate-400"
                  >
                    <span class="text-slate-400 dark:text-slate-500">{{ time(message.sentOn) }}</span>
                    <span class="ml-2 whitespace-pre-wrap break-words">{{ message.body }}</span>
                  </li>
                </ul>
                <p v-else class="mt-2 text-sm text-slate-400 dark:text-slate-500">
                  No client messages before this reply.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">
/* The Card wraps its slot in `.card-text` (h-full), which would overflow a
   fixed-height card body by the title's height — take the remaining space
   instead, so the list below can scroll inside the card. */
:deep(.card-text) {
  height: auto;
  display: flex;
  flex: 1 1 0%;
  flex-direction: column;
  min-height: 0;
}

/* The app's thin slate scrollbar (same as the chat view in Conversation.vue). */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #64748b transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #64748b;
  border-radius: 999px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #475569;
}
</style>
