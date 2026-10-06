<script setup>
import Card from '@/components/Card/index.vue';
import {computed, nextTick, onBeforeUnmount, onMounted, ref, watch} from 'vue';
import {Icon} from '@iconify/vue';
import dateUtils from '@/util/dateUtils';
import TextArea from '@/components/TextArea/index.vue';
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
});

const emit = defineEmits(['sendMessage', 'closeConversation']);

const credentialStore = useCredentialsStore();

const isUser = credentialStore.tokenType === 'user';

const newMessage = ref('');
const timeRefreshKey = ref(0);
let timeRefreshInterval = null;

async function sendMessage() {
  if (newMessage.value.length > 0) {
    emit('sendMessage', props.conversation.id, newMessage.value);
    newMessage.value = '';
  }
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
    chatResizeObserver = new ResizeObserver(updateMaxMessageInputHeight);
    chatResizeObserver.observe(chatBody.value);
  }
});

onBeforeUnmount(() => {
  clearInterval(timeRefreshInterval);
  chatResizeObserver?.disconnect();
});

watch(
  () => props.conversation.messages.length,
  () => {
    scrollToBottom();
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

const conversationTitle = computed(() => {
  const client = props.conversation.initiatorParticipant?.client;

  if (!isUser || !client) {
    return 'BECYCLE';
  }

  return `${client.firstName} ${client.lastName}`;
});

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
            v-for="(message, i) in conversation.messages
              .toSorted((m1, m2) => Date.parse(m1.sentOn) - Date.parse(m2.sentOn))"
            :key="message.id">
            <!-- my messages -->
            <div
              class="flex justify-end group w-full"
              v-if="message.sentByParticipantId === participantId"
            >
              <div class="max-w-[83.333333%] ml-auto">
                <div
                  class="text-content p-3 bg-slate-300 dark:bg-slate-900
                      dark:text-slate-300 text-slate-800 text-sm font-normal
                      rounded-md mb-1 whitespace-pre-wrap break-all"
                >
                  {{ message.body }}
                </div>
                <span class="block text-right font-normal text-xs text-slate-400">
                    {{ getConvenientMessageTime(message.sentOn) }}
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
                  class="text-content p-3 bg-slate-100 dark:bg-slate-600
                      dark:text-slate-300 text-slate-600 text-sm font-normal
                      mb-1 rounded-md whitespace-pre-wrap break-all"
                >
                  {{ message.body }}
                </div>
                <span
                  class="block text-left font-normal text-xs
                      text-slate-400 dark:text-slate-400"
                >
                    {{ getConvenientMessageTime(message.sentOn) }}
                  </span>
              </div>
            </div>
            <!--  other person's messages -->
          </div>
        </template>
      </div>

      <div
        class="chat-footer flex-none max-h-[50%] overflow-hidden md:px-6 px-4 sm:flex md:space-x-4 sm:space-x-2 rtl:space-x-reverse border-t md:pt-6 pt-4 md:pb-6 pb-4 border-slate-100 dark:border-slate-700"
      >
        <div class="flex-1 relative flex space-x-3 rtl:space-x-reverse min-h-0 items-center">
          <TextArea
            :rows="1"
            type="text"
            placeholder="Type your message..."
            classInput="flex-1 m-1 p-2 min-h-[40px] dark:bg-slate-900 rounded-2xl chat-message-input focus:ring-0 focus:outline-0 block w-full bg-transparent dark:text-white resize-none"
            v-model.trim="newMessage"
            autoGrow
            :maxGrowHeight="maxMessageInputHeight"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.enter.shift.exact.prevent="newMessage += '\n'"
          />
          <button
            type="button"
            @click="sendMessage"
            class="h-8 w-8 bg-slate-900 text-white flex flex-col justify-center items-center text-lg rounded-full"
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
</style>
