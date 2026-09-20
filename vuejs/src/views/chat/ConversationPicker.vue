<script setup>
import {ref, defineEmits, computed} from 'vue';
import requests from '@/requests';
import Card from '@/components/Card/index.vue';
import dateUtils from '@/util/dateUtils';
import {Icon} from '@iconify/vue';

const props = defineProps({
  selectedConversation: {
    type: Object,
    required: true,
  },
  myConversation: {
    type: Object,
    required: true,
  },
  conversations: {
    type: Array,
    required: true,
  },
});

const searchTerm = ref('');
const emit = defineEmits(['conversationSelected']);
const filteredConversations = computed(() => {
  return props.conversations
    .filter((c) => c.id !== props.myConversation.id)
    .filter((c) => {
      const name = `${c.initiatorParticipant.client.firstName}} ${c.initiatorParticipant.client.lastName}`;
      return name.toLowerCase().includes(searchTerm.value.toLowerCase());
    })
    .toSorted(
      (c1, c2) =>
        Math.max(...c1.messages.map((m) => Date.parse(m.sentOn))) -
        Math.max(...c2.messages.map((m) => Date.parse(m.sentOn))),
    )
    .reverse();
});

</script>

<template>
  <Card bodyClass=" relative p-0 h-full overflow-hidden " class="h-full">

    <div class="divide-y divide-slate-100 dark:divide-slate-700">
      <div
        v-if="myConversation"
        @click="emit('conversationSelected', myConversation)"
        class="block w-full py-5 focus:ring-0 outline-none cursor-pointer group transition-all
        duration-150 hover:bg-slate-100 dark:hover:bg-slate-600 dark:hover:bg-opacity-70"
      >
        <div class="flex space-x-3 px-6 rtl:space-x-reverse">
          <div class="flex-1 text-start flex">
            <div class="flex-1">
            <span
              class="block text-slate-800 dark:text-slate-300 text-sm font-medium mb-[2px]"
            >
              My Conversation
            </span>
              <span
                class="block text-slate-600 dark:text-slate-300 text-xs font-normal"
              >{{
                  myConversation.messages.length > 0
                    ? myConversation.messages
                      .toSorted((m1, m2) => Date.parse(m1.sentOn) - Date.parse(m2.sentOn))[myConversation.messages.length - 1]
                      .body
                    : '' }}</span
              >
            </div>
            <div class="flex-none ltr:text-right rtl:text-end">
            <span
              class="block text-xs text-slate-400 dark:text-slate-400 font-normal"
            >{{
                myConversation.messages.length > 0
                  ? dateUtils.convertToConvenientString(myConversation.messages
                    .toSorted((m1, m2) => Date.parse(m1.sentOn) - Date.parse(m2.sentOn))[myConversation.messages.length - 1]
                    .sentOn)
                  : '' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="border-b border-slate-100 dark:border-slate-700 py-1">
        <div
          class="search px-3 mx-6 rounded flex items-center space-x-3 rtl:space-x-reverse"
        >
          <div class="flex-none text-base text-slate-900 dark:text-slate-400">
            <Icon icon="bytesize:search" />
          </div>
          <input
            placeholder="Search..."
            v-model="searchTerm"
            class="w-full flex-1 block bg-transparent placeholder:font-normal placeholder:text-slate-400 py-2 focus:ring-0 focus:outline-none dark:text-slate-200 dark:placeholder:text-slate-400"
          />
        </div>
      </div>

      <div class="overflow-y-scroll custom-scrollbar">
      <div
        v-for="(conversation, i) in filteredConversations"
        :key="i"
        @click="$emit('conversationSelected', conversation)"
        class="block w-full py-5 focus:ring-0 outline-none cursor-pointer group transition-all
        duration-150 hover:bg-slate-100 dark:hover:bg-slate-600 dark:hover:bg-opacity-70"
      >
        <div class="flex space-x-3 px-6 rtl:space-x-reverse">
          <div class="flex-1 text-start flex">
            <div class="flex-1">
            <span
              class="block text-slate-800 dark:text-slate-300 text-sm font-medium mb-[2px]"
            >{{ conversation.initiatorParticipant.client.firstName }} {{ conversation.initiatorParticipant.client.lastName }}</span
            >
              <span
                class="block text-slate-600 dark:text-slate-300 text-xs font-normal"
              >{{
                  conversation.messages.length > 0
                    ? conversation.messages
                      .toSorted((m1, m2) => Date.parse(m1.sentOn) - Date.parse(m2.sentOn))[conversation.messages.length - 1]
                      .body
                    : '' }}</span
              >
            </div>
            <div class="flex-none ltr:text-right rtl:text-end">
            <span
              class="block text-xs text-slate-400 dark:text-slate-400 font-normal"
            >{{
                conversation.messages.length > 0
                  ? dateUtils.convertToConvenientString(conversation.messages
                    .toSorted((m1, m2) => Date.parse(m1.sentOn) - Date.parse(m2.sentOn))[conversation.messages.length - 1]
                    .sentOn)
                  : '' }}</span
            >
              <span
                v-if="true"
                class="inline-flex flex-col items-center justify-center text-[10px]
                font-medium w-4 h-4 bg-[#FFC155] text-white rounded-full"
              ></span
              >
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>


<!--    <div class="grid grid-cols-1">-->
<!--      <div-->
<!--        @click="$emit('conversationSelected', myConversation)"-->
<!--        class="col-span-1">-->
<!--        My Conversation-->
<!--      </div>-->
<!--      <div-->
<!--        v-for="conversation in conversations"-->
<!--        :key="conversation.id"-->
<!--        class="col-span-1"-->
<!--        @click="$emit('conversationSelected', conversation)">-->
<!--        {{ conversation.initiatorParticipant.client.firstName }} {{ conversation.initiatorParticipant.client.lastName }}-->
<!--      </div>-->
<!--    </div>-->
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
