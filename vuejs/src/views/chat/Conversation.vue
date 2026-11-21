<script setup>
import Card from '@/components/Card/index.vue';
import {computed, nextTick, onBeforeUnmount, onMounted, ref, watch} from 'vue';
import {Icon} from '@iconify/vue';
import dateUtils from '@/util/dateUtils';
import 'tippy.js/animations/scale.css';
import 'tippy.js/dist/tippy.css';
import TextArea from '@/components/TextArea';
import {useCredentialsStore} from '@/store/credentialsStore';
import {useRouter} from 'vue-router';

const router = useRouter();

const props = defineProps({
  conversation: {
    type: Object,
    required: true,
  },
  participantId: {
    type: String,
    required: true,
  },
  websocketConnected: {
    type: Boolean,
    required: true,
  },
  mySide: {
    type: Function,
    required: true,
  },
  focusMessageId: {
    type: String,
    default: null,
  },
});

const emit = defineEmits(['sendMessage', 'closeConversation', 'markRead']);

const credentialStore = useCredentialsStore();

const isUser = credentialStore.tokenType === 'user';

const newMessage = ref('');
// Keep in sync with the backend's CHAT_MESSAGE_MAX_LENGTH
// (fastapi/app/crud/chats.py): longer messages are rejected there with an
// error frame, so block them here before they are sent.
const MAX_MESSAGE_LENGTH = 2000;

const messageLength = computed(() => newMessage.value.length);
const overLimit = computed(() => messageLength.value > MAX_MESSAGE_LENGTH);
const timeRefreshKey = ref(0);
let timeRefreshInterval = null;

async function sendMessage() {
  if (newMessage.value.length > 0 && !overLimit.value) {
    emit('sendMessage', props.conversation.id, newMessage.value);
    newMessage.value = '';
  }
}

// #511: the "About our AI" disclosure page, opened in a new tab so the
// conversation stays put.
function openAboutOurAi() {
  const {href} = router.resolve({name: 'aboutOurAi'});
  window.open(href, '_blank');
}

const chatHeight = ref(null);
const chatBody = ref(null);
const maxMessageInputHeight = ref(null);
let chatResizeObserver = null;

function updateMaxMessageInputHeight() {
  if (chatBody.value) {
    maxMessageInputHeight.value = Math.floor(chatBody.value.clientHeight / 2);
  }
}

function scrollToBottom() {
  nextTick(() => {
    updateMaxMessageInputHeight();

    if (chatHeight.value) {
      chatHeight.value.scrollTop = chatHeight.value.scrollHeight;
    }
  });
}

onMounted(() => {
  updateMaxMessageInputHeight();

  timeRefreshInterval = setInterval(() => {
    timeRefreshKey.value += 1;
  }, 60000);

  if (chatBody.value) {
    // Only the input's max height reacts to a panel resize. Deliberately NOT
    // scrolling the list here: the observer fires on ANY size change (window
    // resize, scrollbar appearing, the AI-intent popover overflowing the panel
    // while scrolling up — #510), and yanking the list to the newest message
    // there destroys the user's reading position. Auto-scrolling on new
    // messages is the messages.length watch below.
    chatResizeObserver = new ResizeObserver(() => {
      updateMaxMessageInputHeight();
    });
    chatResizeObserver.observe(chatBody.value);
  }
});

onBeforeUnmount(() => {
  clearInterval(timeRefreshInterval);
  chatResizeObserver?.disconnect();
});

let focusHandled = false;

// #510 A-7: the AI-replies audit deep link (/chat?conversation=<id>&focus=<messageId>)
// — scroll to that message once and flash it, instead of the usual
// jump-to-bottom.
function focusMessage() {
  if (focusHandled || !props.focusMessageId) {
    return;
  }
  const el = document.getElementById(`chat-msg-${props.focusMessageId}`);
  if (!el) {
    return; // not rendered yet: retried on the next messages change
  }
  focusHandled = true;
  el.scrollIntoView({behavior: 'smooth', block: 'center'});
  el.classList.add('message-focused');
  setTimeout(() => el.classList.remove('message-focused'), 2000);
}

watch(() => props.focusMessageId, () => {
  focusHandled = false;
});

watch(
  () => props.conversation.messages.length,
  () => {
    if (!focusHandled && props.focusMessageId) {
      nextTick(() => focusMessage());
      return;
    }
    scrollToBottom();
  },
  {immediate: true},
);

watch(
  () => getUnreadMessages(),
  (unReadMessages) => {
    if (unReadMessages.length > 0) {
      emit('markRead', unReadMessages.map((m) => m.id));
    }
  },
  {immediate: true},
);

function viewClient() {
  if (!props.conversation.initiatorParticipant?.client) return;
  const routeData = router.resolve({path: `/clients/${props.conversation.initiatorParticipant.client.id}`});
  window.open(routeData.href, '_blank');
}

function getConvenientMessageTime(sentOn) {
  timeRefreshKey.value;
  return dateUtils.convertToConvenientString(sentOn);
}

// #510 A-1: shown on click of an AI reply — the intent the classification
// recorded (#501 C-7): an intent/FAQ slug, or the "none" sentinel for the
// free-form fallback. Staff only (gated via the v-tippy onShow below).
function intentLabel(message) {
  if (!message.intent || message.intent === 'none') {
    return 'Free-form reply (no intent matched)';
  }
  if (message.intent) {
    return `Detected intent: ${message.intent}`;
  }
  return 'Sent by the workshop assistant (AI)';
}

// Label for staff on their ("my") side: a human staff member's username, so
// they can tell which colleague sent what. AI replies are left to their "AI"
// badge. The other side is the client's — their messages are the only ones
// that can appear there, so it needs no label. Customers (tokenType 'client',
// not isUser) get nothing — their payload carries no nested participants.
function senderLabel(message) {
  if (!isUser) return null;
  const p = message.sentByParticipant;
  if (!p || message.agentSent) return null;
  if (p.user) return p.user.username;
  return null;
}

const conversationTitle = computed(() => {
  const client = props.conversation.initiatorParticipant?.client;

  if (!isUser || !client) {
    return 'BECYCLE';
  }

  return `${client.firstName} ${client.lastName}`;
});

function getUnreadMessages() {
  return props.conversation.messages
    .filter((m) => !props.mySide(m))
    .filter((m) => !m.readOn);
}

</script>

<template>
  <Card bodyClass="relative p-0 h-full overflow-hidden flex flex-col" className="h-full max-h-full overflow-hidden">
    <div ref="chatBody" class="flex flex-col h-full min-h-0">
      <header class="flex-none border-b border-slate-100 dark:border-slate-700">
        <div
          class="flex py-6 md:px-6 px-3 items-center
              text-slate-700 dark:text-slate-300"
        >
          <button
            v-if="isUser"
            type="button"
            class="flex-none w-8 text-left"
            @click="emit('closeConversation')"
          >
            <Icon icon="heroicons-outline:arrow-left" />
          </button>
          <div v-else class="flex-none w-8"></div>

          <div class="flex-1 min-w-0 px-3 truncate">
            {{ conversationTitle }}
          </div>

          <button
            v-if="isUser && conversation.initiatorParticipant?.client"
            type="button"
            class="flex-none w-8 text-right"
            @click="viewClient"
          >
            <Icon icon="heroicons-outline:information-circle" />
          </button>
          <div v-else class="flex-none w-8"></div>
        </div>
      </header>

      <div
        class="flex-1 min-h-0 custom-scrollbar chat-content msgs overflow-y-auto overscroll-y-contain pt-6 space-y-6 pb-4"
        ref="chatHeight"
      >
        <template v-if="conversation.messages.length === 0">
          <div
            class="h-full flex flex-col items-center justify-center xl:space-y-2 space-y-6"
          >
            <img src="@/assets/images/svg/blank.svg" alt="" />
            <h4 class="text-2xl text-slate-600 dark:text-slate-300 font-medium">
              No message yet...
            </h4>

            <p class="text-sm text-slate-500 lg:pt-0 pt-4">
              <span>
                don't worry, just take a deep breath & say "Hello"
              </span>
            </p>
          </div>
        </template>

        <template v-else>
          <div
            class="flex md:px-6 px-4"
            v-for="message in conversation.messages
              .toSorted((m1, m2) => Date.parse(m1.sentOn) - Date.parse(m2.sentOn))"
            :key="message.id"
            :id="`chat-msg-${message.id}`">
            <!-- my messages -->
            <div
              class="flex justify-end group w-full"
              v-if="mySide(message)"
            >
              <div class="max-w-[83.333333%] ml-auto">
                <div
                  v-tippy="{
                    content: intentLabel(message),
                    trigger: 'click',
                    placement: 'top',
                    animation: 'scale',
                    // Staff-only (#510 A-1/A-5): a falsy return from onShow
                    // cancels the show. (Note: `disabled` is NOT a tippy prop —
                    // disable()/enable() are instance methods — so passing it
                    // here is silently ignored.)
                    onShow: () => isUser && message.agentSent,
                    // Keep the popover inside the chat panel: appended to the
                    // page (tippy's default) it would extend the document's
                    // scrollable area whenever it drifts past the panel's
                    // bottom edge while scrolling, growing a page scrollbar —
                    // and the resulting reflow was what kept firing the panel's
                    // ResizeObserver (#510). The card's overflow-hidden then
                    // clips it cleanly at the panel edge instead.
                    appendTo: () => chatBody || document.body,
                  }"
                  :class="`text-content p-3 bg-slate-300 dark:bg-slate-900
                      dark:text-slate-300 text-slate-800 text-sm font-normal
                      rounded-md mb-1 whitespace-pre-wrap break-all
                      ${isUser && message.agentSent ? 'cursor-pointer' : ''}`"
                >
                  {{ message.body }}
                </div>
                <span class="block text-right font-normal text-xs text-slate-400">
                  {{ getConvenientMessageTime(message.sentOn) }}
                  <span v-if="senderLabel(message)" class="ml-1">{{ senderLabel(message) }}</span>
                  <span
                    v-if="message.agentSent"
                    class="ml-2 inline-block align-middle rounded bg-slate-200 dark:bg-slate-700
                             px-1.5 py-0.5 text-[10px] font-semibold leading-none
                             text-slate-500 dark:text-slate-300"
                    title="Sent by the workshop assistant (AI)"
                  >AI</span>
                  <!-- #511 D-1: info affordance next to the AI badge. -->
                  <button
                    v-if="message.agentSent"
                    type="button"
                    class="ml-1 inline-flex items-center align-middle
                           text-slate-400 dark:text-slate-400 hover:text-blue-500 dark:hover:text-blue-400"
                    title="About our AI"
                    @click="openAboutOurAi"
                  >
                    <Icon icon="heroicons-outline:information-circle" class="h-3.5 w-3.5" />
                  </button>
                  <Icon
                    icon="heroicons-outline:check-circle"
                    v-if="message.readOn"
                    class="inline-block align-middle ml-1 h-4 w-4 text-green-500"
                  />
                  </span>
              </div>
            </div>
            <!-- other person's messages -->
            <div
              class="flex justify-start w-full group"
              v-else
            >
              <div class="max-w-[83.333333%] mr-auto">
                <div
                  v-tippy="{
                    content: intentLabel(message),
                    trigger: 'click',
                    placement: 'top',
                    animation: 'scale',
                    // Staff-only (#510 A-1/A-5): a falsy return from onShow
                    // cancels the show. (Note: `disabled` is NOT a tippy prop —
                    // disable()/enable() are instance methods — so passing it
                    // here is silently ignored.)
                    onShow: () => isUser && message.agentSent,
                    // Keep the popover inside the chat panel: appended to the
                    // page (tippy's default) it would extend the document's
                    // scrollable area whenever it drifts past the panel's
                    // bottom edge while scrolling, growing a page scrollbar —
                    // and the resulting reflow was what kept firing the panel's
                    // ResizeObserver (#510). The card's overflow-hidden then
                    // clips it cleanly at the panel edge instead.
                    appendTo: () => chatBody || document.body,
                  }"
                  :class="`text-content p-3 bg-slate-100 dark:bg-slate-600
                      dark:text-slate-300 text-slate-600 text-sm font-normal
                      mb-1 rounded-md whitespace-pre-wrap break-all
                      ${isUser && message.agentSent ? 'cursor-pointer' : ''}`"
                >
                  {{ message.body }}
                </div>
                <span
                  class="block text-left font-normal text-xs
                      text-slate-400 dark:text-slate-400"
                >
                    {{ getConvenientMessageTime(message.sentOn) }}
                    <span
                      v-if="message.agentSent"
                      class="ml-2 inline-block align-middle rounded bg-slate-200 dark:bg-slate-700
                             px-1.5 py-0.5 text-[10px] font-semibold leading-none
                             text-slate-500 dark:text-slate-300"
                      title="Sent by the workshop assistant (AI)"
                    >AI</span>
                    <!-- #511 D-1: info affordance next to the AI badge. -->
                    <button
                      v-if="message.agentSent"
                      type="button"
                      class="ml-1 inline-flex items-center align-middle
                             text-slate-400 dark:text-slate-400 hover:text-blue-500 dark:hover:text-blue-400"
                      title="About our AI"
                      @click="openAboutOurAi"
                    >
                      <Icon icon="heroicons-outline:information-circle" class="h-3.5 w-3.5" />
                    </button>
                  </span>
              </div>
            </div>
            <!--  other person's messages -->
          </div>
        </template>
      </div>

      <div
        class="chat-footer flex-none max-h-[50%] overflow-hidden md:px-6 px-4
            sm:flex md:space-x-4 sm:space-x-2 rtl:space-x-reverse border-t
            md:pt-6 pt-4 md:pb-6 pb-4 border-slate-100 dark:border-slate-700"
      >
        <div class="flex-1 relative flex space-x-3 rtl:space-x-reverse min-h-0 items-center">
            <TextArea
              :rows="1"
              type="text"
              placeholder="Type your message..."
              classInput="flex-1 m-1 p-2 min-h-[40px] dark:bg-slate-900 rounded-2xl chat-message-input focus:ring-0
                focus:outline-0 block w-full bg-transparent dark:text-white resize-none"
              v-model.trim="newMessage"
              autoGrow
              :maxGrowHeight="maxMessageInputHeight"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.enter.shift.exact.prevent="newMessage += '\n'"
              :disabled="!websocketConnected"
            />
          <span
            class="flex-none text-xs tabular-nums"
            :class="overLimit
              ? 'text-danger-500 dark:text-danger-500'
              : 'text-slate-400 dark:text-slate-500'"
          >
            {{ messageLength }} / {{ MAX_MESSAGE_LENGTH }}
          </span>
          <button
            type="button"
            @click="sendMessage"
            class="h-8 w-8 bg-slate-900 text-white flex flex-col justify-center items-center text-lg rounded-full disabled:opacity-50"
            :disabled="!websocketConnected || overLimit"
          >
            <Icon
              icon="heroicons-outline:paper-airplane"
              class="transform rotate-[60deg]"
            />
          </button>
        </div>
      </div>
    </div>
  </Card>
</template>

<style scoped lang="scss">
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

/* #510 A-7: the brief flash marking the audit deep-link target message. */
.message-focused {
  animation: message-flash 2s ease-out;
  border-radius: 0.375rem;
}

@keyframes message-flash {
  from {
    background-color: rgba(59, 130, 246, 0.3);
  }
  to {
    background-color: transparent;
  }
}
</style>
