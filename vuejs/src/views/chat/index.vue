<script setup>
import {useCredentialsStore} from '@/store/credentialsStore';
import Conversation from '@/views/chat/Conversation.vue';
import ConversationPicker from '@/views/chat/ConversationPicker.vue';
import {computed, reactive, ref, watch} from 'vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Alert from '@/components/Alert/index.vue';

const toast = useToast();
const credentialStore = useCredentialsStore();

const isUser = credentialStore.tokenType === 'user';

const conversations = ref([]);

const selectedConversation = ref(null);
const participantId = ref(null);


const myConversation = computed({
  get() {
    return conversations.value.find((c) => c.initiatorParticipantId === participantId.value);
  },
});


function selectConversation(conversation) {
  selectedConversation.value = conversation;
}

requests.getParticipantMe().then((response) => {
  participantId.value = response.data.id;
});
const websocketStatus = ref(0);


let websocket = null;
let wait = 500;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function connect() {
  console.log('connecting');
  websocket = new WebSocket('ws://localhost:8000/chats/ws');

  websocket.onopen = async (ev) => {
    console.log('websocket opened');
    wait = 500;
    websocket.send(JSON.stringify({
      token: credentialStore.token,
    }));

    requests.getMyConversation().then((response) => {
      selectConversation(response.data);
      conversations.value.push(response.data);
      subscribeToConversations([selectedConversation.value.id]);
    });

    if (isUser) {
      requests.getConversations().then((response) => {
        conversations.value.push(...response.data);
        subscribeToConversations(conversations.value.map((c) => c.id));
      });
    }
  };

  websocket.onmessage = (d) => {
    // console.log(d);
    const message = JSON.parse(d.data);
    console.log({message, myConversation: myConversation.value});

    conversations.value.forEach((c) => {
      if (c.id === message.conversationId) {
        c.messages.push(message);
      }
    });
  };

  websocket.onclose = async (ev) => {
    console.log('websocket closed');
    console.log('sleeping', wait);
    await sleep(wait);
    connect();
    wait *= 2;
  };
}

connect();

function sendMessage(conversationId, message) {
  websocket.send(JSON.stringify({
    command: 'message',
    payload: {
      conversationId: conversationId,
      body: message,
    },
  }));
}

function subscribeToConversations(conversationIds) {
  websocket.send(JSON.stringify({
    command: 'subscribe',
    payload: {
      conversationIds: conversationIds,
    },
  }));
}

setInterval(() => {
  websocketStatus.value = websocket.readyState;
}, 500);

const websocketStatusReadable = computed(() => {
  switch (websocketStatus.value) {
  case 0:
    return {value: 'warning-outline', label: 'Connecting...'};
  case 1:
    return {value: 'success-outline', label: 'Connected'};
  case 2:
    return {value: 'info-outline', label: 'Disconnecting...'};
  case 3:
    return {value: 'danger-outline', label: 'Disconnected'};
  }
});


</script>

<template>
    <div class="flex flex-col gap-5 h-full min-h-0">
      <div>
        <Alert
          :type="websocketStatusReadable.value"
        >{{websocketStatusReadable.label}}</Alert>
      </div>
      <div class="flex gap-5 flex-1 min-h-0">
        <template v-if="isUser">
          <div class="basis-1/4 basis min-h-0">
            <ConversationPicker
              v-if="myConversation"
              :selectedConversation="selectedConversation"
              @conversation-selected="selectConversation"
              :conversations="conversations"
              :myConversation="myConversation"
            />
          </div>
        </template>
        <div
          v-if="selectedConversation"
          :class="`${isUser ? 'basis-3/4' : 'basis-full'} min-h-0`">
          <Conversation
            :conversation="selectedConversation"
            :participantId="participantId"
            @send-message="sendMessage"
          />
        </div>
      </div>
      
    </div>

</template>

<style scoped lang="scss">

</style>
