<script setup>
import {useCredentialsStore} from '@/store/credentialsStore';
import Conversation from '@/views/chat/Conversation.vue';
import ConversationPicker from '@/views/chat/ConversationPicker.vue';
import {computed, onBeforeUnmount, ref} from 'vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Alert from '@/components/Alert/index.vue';

const API_WS_PROTOCOL = import.meta.env.VITE_API_WS_PROTOCOL;
const API_HOST = import.meta.env.VITE_API_HOST;
const API_PORT = import.meta.env.VITE_API_PORT;
const API_SUBDIR = import.meta.env.VITE_API_SUBDIR;

const toast = useToast();
const credentialStore = useCredentialsStore();

const isUser = credentialStore.tokenType === 'user';

const conversations = ref([]);

const selectedConversation = ref(null);
const participantId = ref(null);
const websocketStatus = ref(0);

const wsBaseUrl = `${API_WS_PROTOCOL}://${API_HOST}:${API_PORT}${API_SUBDIR}/chats/ws`;
let retryWait = 500;
const pingTime = 10000;
let retryTimeout = null;
const pongReceived = ref(true);
const connecting = ref(false);
let heartbeat = null;

const myConversation = computed({
  get() {
    return conversations.value.find((c) => c.initiatorParticipantId === participantId.value);
  },
});

function selectConversation(conversation) {
  selectedConversation.value = conversation;
}

let websocket = null;

Promise.all([requests.getParticipantMe(), requests.getMyConversation(), ...(isUser ? [requests.getConversations()] : [])])
  .then(([participantResponse, myConversationResponse, conversationsResponse]) => {
    conversations.value.splice(0, conversations.value.length);

    participantId.value = participantResponse.data.id;
    selectConversation(myConversationResponse.data);
    conversations.value.push(myConversationResponse.data);

    if (isUser && conversationsResponse) {
      conversations.value.push(...conversationsResponse.data);
    }

    console.log('replacing websocket');
    websocket = createWebsocket();
  });


function createWebsocket() {
  console.log('creating websocket');
  const _websocket = new WebSocket(wsBaseUrl);

  _websocket.onopen = async (ev) => {
    await connect();
  };

  _websocket.onmessage = (d) => {
    if (d.data === 'pong') {

    } else {
      const message = JSON.parse(d.data);
      if (message.command === 'pong') {
        pongReceived.value = true;
        retryWait = 500;
      } else if (message.command === 'message') {
        conversations.value.forEach((c) => {
          if (c.id === message.payload.conversationId) {
            c.messages.push(message.payload);
          }
        });
      }
    }
  };

  _websocket.onerror = async (ev) => {
    retryTimeout = setTimeout(connect, retryWait);
  };

  _websocket.onclose = async (ev) => {
    console.log('clearing heartbeat and retry');
    clearInterval(heartbeat);
    clearTimeout(retryTimeout);
    retryTimeout = setTimeout(() => {
      console.log('creating new websocket');
      websocket = createWebsocket();
    }, retryWait);
  };

  return _websocket;
}

async function connect() {
  retryWait *= 1.5;
  connecting.value = true;
  console.log('Connecting...');
  clearTimeout(retryTimeout);
  clearInterval(heartbeat);

  websocket.send(JSON.stringify({
    token: credentialStore.token,
  }));

  pongReceived.value = true;
  heartbeat = setInterval(() => {
    if (!pongReceived.value) {
      console.log('closing websocket');
      websocket.close();
      clearInterval(heartbeat);
      // Trigger reconnection logic
      return;
    }
    pongReceived.value = false;
    websocket.send(JSON.stringify({command: 'ping'}));
  }, pingTime);


  subscribeToConversations([selectedConversation.value.id]);
  if (isUser) {
    subscribeToConversations(conversations.value.map((c) => c.id));
  }
  setTimeout(() => connecting.value = false, 500);
}

function sendWebsocketCommand(command, payload) {
  websocket.send(JSON.stringify({
    command: command,
    payload: payload,
  }));
}

function sendMessage(conversationId, message) {
  sendWebsocketCommand('message', {
    conversationId: conversationId,
    body: message,
  });
}

function subscribeToConversations(conversationIds) {
  sendWebsocketCommand('subscribe', {
    conversationIds: conversationIds,
  });
}

setInterval(() => {
  websocketStatus.value = websocket.readyState;
  console.log('websocket status', websocketStatus.value);
}, 1000);

const websocketStatusReadable = computed(() => {
  if (connecting.value) {
    return {value: 'warning-outline', label: 'Connecting...'};
  } else if (!pongReceived.value) {
    return {value: 'danger-outline', label: 'Disconnected'};
  }
  switch (websocketStatus.value) {
  case 0:
    return {value: 'warning-outline', label: 'Connecting...'};
  case 1:
    return {value: 'success-outline', label: 'Connected'};
  case 2:
    return {value: 'info-outline', label: 'Disconnecting...'};
  case 3:
    return {value: 'danger-outline', label: 'Disconnected'};
  default:
    return {value: 'danger-outline', label: 'Unknown'};
  }
});

onBeforeUnmount(() => {
  clearInterval(heartbeat);
  clearInterval(retryTimeout);
  websocket.onclose = async () => {};
  console.log('websocket closed');
  websocket.close();
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
          <div class="basis-1/4 basis min-h-0 min-w-0 overflow-hidden">
            <ConversationPicker
              v-if="myConversation"
              :selectedConversation="selectedConversation"
              @conversation-selected="selectConversation"
              :conversations="conversations"
              :myConversation="myConversation"
              :participantId="participantId"
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
