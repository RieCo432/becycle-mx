<script>
import Card from '@/components/Card/index.vue';
import {Icon} from '@iconify/vue';
import {debounce} from 'lodash-es';
import requests from '@/requests';
import dateUtils from '@/util/dateUtils';

const REPLY_BATCH = 50;

export default {
  name: 'aiReplies',
  components: {Card, Icon},
  data() {
    return {
      initialLoading: true,
      entries: [],
      loadError: null,
      search: '',
    };
  },
  created() {
    // #510 A-6, the client/bike-search pattern: typing filters what is
    // already loaded instantly; a debounced refetch then fetches the
    // newest 50 matches so searches reach beyond the initial batch. (The
    // server matches exactly the same visible fields, so its results always
    // pass the client filter — nothing vanishes and pops back.)
    this.runSearch = debounce(this.runSearch, 500, {leading: false, trailing: true});
    this.load();
  },
  beforeUnmount() {
    this.runSearch.cancel();
  },
  watch: {
    search() {
      this.runSearch();
    },
  },
  computed: {
    replyBatch() {
      return REPLY_BATCH;
    },
    visibleEntries() {
      const term = this.search.trim().toLowerCase();
      if (!term) {
        return this.entries;
      }
      // Instant client-side preview; the server refetch (same visible
      // fields) lands as the authoritative result set.
      return this.entries.filter((entry) => this.matches(entry, term));
    },
  },
  methods: {
    load() {
      this.initialLoading = true;
      requests.getAiReplies(undefined, REPLY_BATCH).then((response) => {
        this.entries = response.data;
        this.loadError = null;
      }).catch((error) => {
        // 403 (not an admin) already toasts globally via validateStatus —
        // this is the in-page state for that and any other failure.
        this.loadError = error.response?.data?.detail?.description ?? 'AI replies could not be loaded.';
      }).finally(() => {
        this.initialLoading = false;
      });
    },
    runSearch() {
      const term = this.search.trim();
      requests.getAiReplies(term || undefined, REPLY_BATCH).then((response) => {
        // Ignore stale responses from faster typing — a newer query superseded it.
        if (this.search.trim() !== term) {
          return;
        }
        this.entries = response.data;
        this.loadError = null;
      }).catch((error) => {
        if (this.search.trim() !== term) {
          return;
        }
        this.loadError = error.response?.data?.detail?.description ?? 'AI replies could not be loaded.';
      });
    },
    // #510 A-7: open the conversation in the chat view (new tab, so the
    // audit page stays put for further review), scrolled to and
    // highlighting this AI reply.
    openInChat(entry) {
      const {href} = this.$router.resolve({
        path: '/chat',
        query: {conversation: entry.conversationId, focus: entry.id},
      });
      window.open(href, '_blank');
    },
    // Client-side preview filter (#510 A-6): the same visible fields the
    // server matches — reply text, intent, shown context, name/email.
    matches(entry, term) {
      const haystacks = [
        entry.body,
        entry.intent,
        `${entry.client.firstName} ${entry.client.lastName}`,
        entry.client.emailAddress,
        ...entry.context.map((message) => message.body),
      ];
      return haystacks.some((haystack) => (haystack ?? '').toLowerCase().includes(term));
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
          The most recent {{ replyBatch }} replies the workshop assistant sent in client conversations —
          each with the detected intent and the client messages that prompted it.
          Search by reply text, detected intent, client message text, or client name/email.
        </p>

        <div class="flex-none relative mb-4">
          <input
            v-model.trim="search"
            type="text"
            placeholder="Search replies, intent, client messages, client name or email…"
            class="w-full p-2 pl-9 pr-8 text-sm bg-slate-100 dark:bg-slate-900
                   border border-slate-200 dark:border-slate-700 rounded-md
                   focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <Icon
            icon="heroicons-outline:magnifying-glass"
            class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none"
          />
          <button
            v-if="search"
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            @click="search = ''"
          >
            <Icon icon="heroicons-outline:x-circle" class="h-4 w-4" />
          </button>
        </div>

        <div class="custom-scrollbar flex-1 min-h-0 overflow-y-auto">
          <div
            v-if="initialLoading"
            class="py-8 text-center text-sm text-slate-500 dark:text-slate-400"
          >
            Loading…
          </div>

          <div v-else-if="loadError" class="py-8 text-center text-sm text-danger-500 dark:text-danger-500">
            {{ loadError }}
          </div>

          <div
            v-else-if="visibleEntries.length === 0"
            class="py-8 text-center text-sm text-slate-500 dark:text-slate-400"
          >
            {{ search.trim() ? 'No AI replies match your search.' : 'No AI replies in client conversations yet.' }}
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="entry in visibleEntries"
              :key="entry.id"
              class="border border-slate-100 dark:border-slate-700 rounded-md p-4"
            >
              <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
                <span class="font-semibold text-slate-800 dark:text-slate-200">
                  {{ entry.client.firstName }} {{ entry.client.lastName }}
                </span>
                <span class="text-slate-400">{{ entry.client.emailAddress }}</span>
                <span class="text-slate-400">{{ time(entry.sentOn) }}</span>
                <span
                  class="inline-block align-middle rounded bg-slate-200 dark:bg-slate-700
                         px-1.5 py-0.5 text-[10px] font-semibold leading-none
                         text-slate-500 dark:text-slate-300"
                  :title="`Detected intent: ${entry.intent ?? '—'}`"
                >{{ intentLabel(entry) }}</span>
                <button
                  type="button"
                  class="ml-auto inline-flex items-center gap-1 rounded px-2 py-1 text-xs
                         text-slate-500 dark:text-slate-400
                         border border-slate-200 dark:border-slate-700
                         hover:bg-slate-100 dark:hover:bg-slate-800"
                  @click="openInChat(entry)"
                >
                  <Icon icon="heroicons-outline:chat-bubble-left-right" class="h-3.5 w-3.5" />
                  Open in chat
                </button>
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
