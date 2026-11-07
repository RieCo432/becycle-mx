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
const RETRY_BASE = 500;
const RETRY_MAX = 10000;
let retryWait = RETRY_BASE;
const pingTime = 10000;
let retryTimeout = null;
let heartbeat = null;
let pongMissedTimeout = null;

const myConversation = computed({
  get() {
    return conversations.value.find((c) => c.initiatorParticipantId === participantId.value);
  },
});

function selectConversation(conversation) {
  selectedConversation.value = conversation;
}

let websocket = null;

Promise.all([
  requests.getParticipantMe(),
  requests.getMyConversation(),
  ...(isUser ? [requests.getConversations()] : [])])
  .then(([participantResponse, myConversationResponse, conversationsResponse]) => {
    conversations.value.splice(0, conversations.value.length);

    participantId.value = participantResponse.data.id;
    if (!isUser) {
      selectConversation(myConversationResponse.data);
    }

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

  _websocket.onopen = () => {
    // a socket that opened is healthy: reset the backoff
    retryWait = RETRY_BASE;
    connect(_websocket);
  };

  _websocket.onmessage = (d) => {
    if (d.data === 'pong') {

    } else {
      const message = JSON.parse(d.data);
      if (message.command === 'pong') {
        clearTimeout(pongMissedTimeout);
        retryWait = RETRY_BASE;
      } else if (message.command === 'message') {
        const convo = conversations.value.find((c) => c.id === message.payload.conversationId);
        convo?.messages.push(message.payload);
        if (
          message.payload.conversationId !== selectedConversation.value?.id &&
          message.payload.sentByParticipantId !== participantId.value
        ) {
          const client = convo.initiatorParticipant.client;
          toast.info(
            `${client?.firstName} ${client?.lastName}: ${message.payload.body.slice(0, 160)}`,
            {timeout: 2000});
        }
      } else if (message.command === 'error') {
        if (message.payload?.command === 'message') {
          toast.error('Message could not be sent. Please reload and try again.', {timeout: 4000});
        } else {
          toast.error('Some conversations could not be opened.', {timeout: 4000});
        }
      }
    }
  };

  // onclose is the single reconnection driver: the browser always fires it
  // (after onerror) for a failed socket, and it also follows our own
  // deliberate closes (heartbeat timeout). Scheduling a reconnect from
  // onerror as well let two reconnectors race, and a stale connect() would
  // double-send token+subscribes onto the replacement socket.
  _websocket.onerror = (ev) => {
    console.log('websocket error; onclose will reconnect');
  };

  _websocket.onclose = (ev) => {
    console.log('clearing heartbeat and retry');
    clearInterval(heartbeat);
    clearTimeout(pongMissedTimeout);
    if (retryTimeout) {
      clearTimeout(retryTimeout);
    }
    const wait = retryWait;
    retryWait = Math.min(Math.round(retryWait * 1.5), RETRY_MAX);
    retryTimeout = setTimeout(() => {
      retryTimeout = null;
      console.log('creating new websocket');
      websocket = createWebsocket();
    }, wait);
  };

  return _websocket;
}

function connect(ws) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    // socket went away between open and now: force the reconnect path
    if (ws) {
      ws.close();
    }
    return;
  }
  console.log('Connecting...');
  clearInterval(heartbeat);

  ws.send(JSON.stringify({
    token: credentialStore.token,
  }));

  heartbeat = setInterval(() => {
    pongMissedTimeout = setTimeout(() => {
      toast.warning('Connection issues...', {timeout: 2000});
      console.log('closing unresponsive websocket');
      ws.close(); // onclose handles the reconnect
      clearInterval(heartbeat);
    }, 2000);
    ws.send(JSON.stringify({command: 'ping'}));
  }, pingTime);

  // selectedConversation may be null (conversation closed) — previously this
  // threw after the heartbeat started, leaving the socket connected but
  // subscribed to nothing.
  if (selectedConversation.value) {
    subscribeToConversations([selectedConversation.value.id]);
  }
  if (isUser) {
    subscribeToConversations(conversations.value.map((c) => c.id));
  }
}

function sendWebsocketCommand(command, payload) {
  // the socket may be closed/reconnecting when the user acts; sending on a
  // non-open socket throws InvalidStateError
  if (!websocket || websocket.readyState !== WebSocket.OPEN) {
    console.log('websocket not open; dropping', command);
    return;
  }
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

function closeConversation() {
  selectedConversation.value = null;
}

let websocketStatusInterval = null;

websocketStatusInterval = setInterval(() => {
  websocketStatus.value = websocket?.readyState;
  console.log('websocket status', websocketStatus.value);
}, 1000);

const websocketStatusReadable = computed(() => {
  switch (websocketStatus.value) {
  case 0:
    return {value: 'warning-outline', label: 'Connecting...'};
  case 1:
    return {value: 'success-outline', label: 'Connected'};
  case 2:
  case 3:
    return {value: 'danger-outline', label: 'Disconnected'};
  default:
    return {value: 'danger-outline', label: 'Unknown'};
  }
});

const showConversationPicker = computed(() => {
  return isUser && !selectedConversation.value;
});

onBeforeUnmount(() => {
  clearInterval(heartbeat);
  clearTimeout(retryTimeout);
  clearInterval(websocketStatusInterval);
  if (websocket) {
    websocket.onclose = async () => {};
    websocket.close();
    console.log('websocket closed');
  }
});


</script>

<template>
  <div class="relative flex flex-col gap-5 h-full min-h-0">
    <Alert
      v-if="websocketStatus !== 1"
      :type="websocketStatusReadable.value"
    >{{websocketStatusReadable.label}}</Alert>
      <div class="flex gap-5 flex-1 min-h-0">
        <template v-if="isUser && myConversation && participantId">
          <div
            :class="`basis min-h-0 min-w-0 overflow-hidden
            ${showConversationPicker ? 'basis-full  ' : 'hidden md:flex'}
            md:basis-6/12 lg:basis-5/12 2xl:basis-3/12`">
            <ConversationPicker
              :selectedConversation="selectedConversation"
              @conversation-selected="selectConversation"
              :conversations="conversations"
              :myConversation="myConversation"
              :participantId="participantId"
            />
          </div>
        </template>
        <div
          v-if="selectedConversation && participantId"
          :class="`${showConversationPicker ? 'md:basis-6/12 lg:basis-7/12 2xl:basis-9/12' : 'basis-full'} min-h-0`">
          <Conversation
            :conversation="selectedConversation"
            :participantId="participantId"
            @send-message="sendMessage"
            @close-conversation="closeConversation"
            :websocketConnected="websocketStatus === 1"
          />
        </div>
      </div>

    </div>

</template>

<style scoped lang="scss">

</style>
