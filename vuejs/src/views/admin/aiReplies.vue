<script>
import Card from '@/components/Card/index.vue';
import {Icon} from '@iconify/vue';
import {debounce} from 'lodash-es';
import {useToast} from 'vue-toastification';
import requests from '@/requests';
import dateUtils from '@/util/dateUtils';

const toast = useToast();

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
      // #510 A-8: '' = all, otherwise 'unrated' | 'good' | 'not-good'.
      ratingFilter: '',
      ratingFilters: [
        {value: '', label: 'All'},
        {value: 'unrated', label: 'Unrated'},
        {value: 'good', label: 'Good'},
        {value: 'not-good', label: 'Not good'},
      ],
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
    // The displayed list: the fetched entries narrowed by the active
    // rating filter and the current search term (an instant preview until
    // the debounced refetch lands). Purely derived — rating a reply
    // re-derives the list, so it falls out of an active filter on its own.
    visibleEntries() {
      const term = this.search.trim().toLowerCase();
      return this.entries.filter((entry) => {
        if (!this.matchesRatingFilter(entry.qualityRating)) {
          return false;
        }
        if (term && !this.matches(entry, term)) {
          return false;
        }
        return true;
      });
    },
  },
  methods: {
    load() {
      this.initialLoading = true;
      requests.getAiReplies(undefined, REPLY_BATCH, this.ratingFilter || undefined).then((response) => {
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
      requests.getAiReplies(term || undefined, REPLY_BATCH, this.ratingFilter || undefined).then((response) => {
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
        // A failed search toasts rather than swapping the list for an error
        // state — the last successful results stay visible.
        toast.error(error.response?.data?.detail?.description ?? 'AI replies could not be loaded.', {timeout: 2000});
      });
    },
    setRatingFilter(value) {
      this.ratingFilter = value;
      this.load();
    },
    // #510 A-8: the rating button's styling — highlighted when that rating
    // is active, plain otherwise (neither highlighted = unrated).
    ratingButtonClass(entry, rating) {
      // Not active (including unrated): plain slate button.
      const inactive = [
        'text-slate-500', 'dark:text-slate-400',
        'border-slate-200', 'dark:border-slate-700',
        'hover:bg-slate-100', 'dark:hover:bg-slate-800',
      ].join(' ');
      if (entry.qualityRating !== (rating === 'good')) {
        return inactive;
      }
      if (rating === 'good') {
        return 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 border-green-300 dark:border-green-700 font-semibold';
      }
      return 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 border-red-300 dark:border-red-700 font-semibold';
    },
    // #510 A-8: set the rating, or clear it by clicking the active one.
    rate(entry, rating) {
      const next = (
        (rating === 'good' && entry.qualityRating === true) ||
        (rating === 'not-good' && entry.qualityRating === false)
      ) ? 'unrated' : rating;
      requests.rateAiReply(entry.id, next).then((response) => {
        // visibleEntries re-derives from this: if the rating moved the
        // reply out of the active filter (e.g. rating while "Unrated" is
        // selected), it falls out of the list automatically.
        entry.qualityRating = response.data.qualityRating;
      }).catch((error) => {
        toast.error(error.response?.data?.detail?.description ?? 'Rating could not be saved.', {timeout: 4000});
      });
    },
    // #510 A-8: does a rating value pass the active filter ('' = all)?
    matchesRatingFilter(value) {
      switch (this.ratingFilter) {
      case 'unrated':
        return value === null;
      case 'good':
        return value === true;
      case 'not-good':
        return value === false;
      default:
        return true;
      }
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
          Search by reply text, detected intent, client message text, or client name/email,
          or filter by the good/not-good rating.
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

        <!-- #510 A-8: filter by quality rating (All / Unrated / Good / Not good). -->
        <div class="flex-none flex flex-wrap gap-1 mb-4">
          <button
            v-for="option in ratingFilters"
            :key="option.value"
            type="button"
            class="rounded px-2 py-1 text-xs"
            :class="ratingFilter === option.value
              ? 'bg-slate-200 dark:bg-slate-700 font-semibold text-slate-800 dark:text-slate-200'
              : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'"
            @click="setRatingFilter(option.value)"
          >
            {{ option.label }}
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
            {{ search.trim() || ratingFilter
              ? 'No AI replies match your filters.'
              : 'No AI replies in client conversations yet.' }}
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
                <span class="ml-auto flex items-center gap-1">
                  <!-- #510 A-8: rate good / not good; clicking the active one clears it.
                       Hidden (not just disabled) when the user lacks the POST
                       permission, in case a read-only audit role ever exists. -->
                  <button
                    v-if="$can('postRateAiReply')"
                    type="button"
                    class="rounded px-2 py-1 text-xs border"
                    :class="ratingButtonClass(entry, 'good')"
                    :title="entry.qualityRating === true ? 'Rated good - click to clear' : 'Rate as good'"
                    @click="rate(entry, 'good')"
                  >
                    Good
                  </button>
                  <button
                    v-if="$can('postRateAiReply')"
                    type="button"
                    class="rounded px-2 py-1 text-xs border"
                    :class="ratingButtonClass(entry, 'not-good')"
                    :title="entry.qualityRating === false ? 'Rated not good - click to clear' : 'Rate as not good'"
                    @click="rate(entry, 'not-good')"
                  >
                    Not good
                  </button>
                  <button
                    type="button"
                    class="inline-flex items-center gap-1 rounded px-2 py-1 text-xs
                           text-slate-500 dark:text-slate-400
                           border border-slate-200 dark:border-slate-700
                           hover:bg-slate-100 dark:hover:bg-slate-800"
                    @click="openInChat(entry)"
                  >
                    <Icon icon="heroicons-outline:chat-bubble-left-right" class="h-3.5 w-3.5" />
                    Open in chat
                  </button>
                </span>
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
