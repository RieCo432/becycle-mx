<script setup>
import Card from '@/components/Card/index.vue';
import {nextTick, onBeforeUnmount, onMounted, ref, watch} from 'vue';
import {Icon} from '@iconify/vue';
import dateUtils from '@/util/dateUtils';
import TextArea from '@/components/TextArea/index.vue';

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
const emit = defineEmits(['sendMessage']);

const newMessage = ref('');

async function sendMessage() {
  emit('sendMessage', props.conversation.id, newMessage.value);
  newMessage.value = '';
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

  if (chatBody.value) {
    chatResizeObserver = new ResizeObserver(updateMaxMessageInputHeight);
    chatResizeObserver.observe(chatBody.value);
  }
});

onBeforeUnmount(() => {
  chatResizeObserver?.disconnect();
});

watch(
  () => props.conversation.messages.length,
  () => {
    scrollToBottom();
  },
  {immediate: true},
);

</script>

<template>
  <Card bodyClass="relative p-0 h-full overflow-hidden flex flex-col" className="h-full max-h-full overflow-hidden">
    <div ref="chatBody" class="flex flex-col h-full min-h-0">
      <header class="flex-none border-b border-slate-100 dark:border-slate-700">
        <div class="flex py-6 md:px-6 px-3 items-center">
          <div
            class="flex-none flex md:space-x-3 space-x-1 items-center rtl:space-x-reverse"
          >
            Something
          </div>
        </div>
      </header>

      <div
        class="flex-1 min-h-0 custom-scrollbar chat-content msgs overflow-y-auto pt-6 space-y-6 pb-4"
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
            class="block md:px-6 px-4"
            v-for="(message, i) in conversation.messages
              .toSorted((m1, m2) => Date.parse(m1.sentOn) - Date.parse(m2.sentOn))"
            :key="i">
            <div
              class="flex space-x-2 items-start justify-end group w-full rtl:space-x-reverse"
              v-if="message.sentByParticipantId === participantId"
            >
              <div class="no flex space-x-4 rtl:space-x-reverse">
                <div
                  class="opacity-0 invisible group-hover:opacity-100 group-hover:visible"
                >
                </div>
                <div class="whitespace-pre-wrap break-all">
                  <div
                    class="text-contrent p-3 bg-slate-300 dark:bg-slate-900 dark:text-slate-300 text-slate-800 text-sm font-normal rounded-md flex-1 mb-1"
                  >
                    {{ message.body }}
                  </div>
                  <span class="font-normal text-xs text-slate-400">
                    {{  dateUtils.convertToConvenientString(message.sentOn) }}
                  </span>
                </div>
              </div>
            </div>
            <!-- me  -->
            <div
              class="flex space-x-2 items-start group rtl:space-x-reverse"
              v-else
            >
              <div class="flex-1 flex space-x-4 rtl:space-x-reverse">
                <div>
                  <div
                    class="text-contrent p-3 bg-slate-100 dark:bg-slate-600 dark:text-slate-300 text-slate-600 text-sm font-normal mb-1 rounded-md flex-1 whitespace-pre-wrap break-all"
                  >
                    {{ message.body }}
                  </div>
                  <span
                    class="font-normal text-xs text-slate-400 dark:text-slate-400">
                    {{  dateUtils.convertToConvenientString(message.sentOn) }}
                  </span>
                </div>
                <div
                  class="opacity-0 invisible group-hover:opacity-100 group-hover:visible"
                >
                </div>
              </div>
            </div>
            <!-- sender -->
          </div>
        </template>
      </div>

      <div
        class="chat-footer flex-none max-h-[50%] overflow-hidden md:px-6 px-4 sm:flex md:space-x-4 sm:space-x-2 rtl:space-x-reverse border-t md:pt-6 pt-4 md:pb-6 pb-4 border-slate-100 dark:border-slate-700"
      >
        <div class="flex-1 relative flex space-x-3 rtl:space-x-reverse min-h-0 items-center">
          <TextArea
            rows="1"
            type="text"
            placeholder="Type your message..."
            classInput="flex-1 m-1 p-2 min-h-0 dark:bg-slate-900 rounded-2xl chat-message-input focus:ring-0 focus:outline-0 block w-full bg-transparent dark:text-white resize-none"
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
