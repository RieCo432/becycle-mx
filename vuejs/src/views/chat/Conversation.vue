<script setup>


import Card from '@/components/Card/index.vue';
import {ref} from 'vue';
import {Icon} from '@iconify/vue';

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

const newMessage = ref('');

async function sendMessage() {
  newMessage.value = '';
}


</script>

<template>
  <Card bodyClass="p-0 h-full" class="h-full">
    <div>
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
        don't worry, just take a deep breath & say "Hello"</span
      >
          </p>
        </div>
      </template>
      <template v-else>
        <div class="h-full">
          <header class="border-b border-slate-100 dark:border-slate-700">
            <div class="flex py-6 md:px-6 px-3 items-center">
              <div
                class="flex-none flex md:space-x-3 space-x-1 items-center rtl:space-x-reverse"
              >
                Something
              </div>
            </div>
          </header>
          <div class="chat-content parent-height">
            <div
              class="msgs overflow-y-auto msg-height pt-6 space-y-6"
              ref="chatheight"
            >
              <div class="block md:px-6 px-4" v-for="(message, i) in conversation.messages" :key="i">

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
                          time
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
                        class="font-normal text-xs text-slate-400 dark:text-slate-400"
                      >12:20 pm</span
                      >
                    </div>
                    <div
                      class="opacity-0 invisible group-hover:opacity-100 group-hover:visible"
                    >

                    </div>
                  </div>
                </div>
                <!-- sender -->
                
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
    
    <div
      class="md:px-6 px-4 sm:flex md:space-x-4 sm:space-x-2 rtl:space-x-reverse border-t md:pt-6 pt-4 border-slate-100 dark:border-slate-700"
    >
      <div class="flex-1 relative flex space-x-3 rtl:space-x-reverse">
        <div class="flex-1 dark:bg-slate-900 rounded-full p-1">
          <textarea
            type="text"
            placeholder="Type your message..."
            class="focus:ring-0 focus:outline-0 block w-full bg-transparent dark:text-white  resize-none"
            v-model.trim="newMessage"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.enter.shift.exact.prevent="newMessage += '\n'"
          />
        </div>
        <div class="flex-none md:pr-0 pr-3">
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

</style>