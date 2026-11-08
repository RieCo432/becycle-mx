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
// close code the server uses when the token is rejected — retrying with the
// same token can never succeed, so this stops the reconnect loop
const WS_CLOSE_AUTH_FAILED = 4401;
let retryWait = RETRY_BASE;
const pingTime = 10000;
let retryTimeout = null;
let heartbeat = null;
let pongMissedTimeout = null;
// true once the user leaves the page; onclose must not schedule a reconnect
let isLeaving = false;

let unauthorizedWarned = false;
function showUnauthorizedWarning() {
  if (unauthorizedWarned) {
    return;
  }
  unauthorizedWarned = true;
  toast.error('Your login has expired. Please sign in again.', {timeout: 10000});
}

const myConversation = computed({
  get() {
    return conversations.value.find((c) => c.initiatorParticipantId === participantId.value);
  },
});

function selectConversation(conversation) {
  selectedConversation.value = conversation;
  // make sure we are actually subscribed (the conversation may have appeared
  // after the socket connected); the server's subscribe is idempotent
  subscribeToConversations([conversation.id]);
}

// A client's conversation comes into existence the moment they first open
// the chat view (the server get-or-creates it), and the server pushes it
// over the websocket (command: 'conversation'). This one-shot catch-up
// refetch runs on every (re)connect and covers the window in which this
// socket was disconnected when the conversation was created (the push was
// then missed).
async function refreshConversations() {
  if (!isUser) {
    return;
  }
  const response = await requests.getConversations();
  const known = new Set(conversations.value.map((c) => c.id));
  const newConversations = response.data.filter((c) => !known.has(c.id));
  if (newConversations.length) {
    conversations.value.push(...newConversations);
    // subscribe, or the newcomer's messages are invisible until a reload
    subscribeToConversations(newConversations.map((c) => c.id));
  }
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
    } else if (message.command === 'conversation') {
      // a conversation was just created (a client opened the chat view for
      // the first time): show it in the picker and start receiving its
      // messages
      const existing = conversations.value.find((c) => c.id === message.payload.id);
      if (!existing) {
        conversations.value.push(message.payload);
      }
      subscribeToConversations([message.payload.id]);
    } else if (message.command === 'error') {
      if (message.payload?.reason === 'unauthorized') {
        // the token was rejected; the socket is being closed with the
        // terminal code, and onclose will stop the reconnect loop
        showUnauthorizedWarning();
      } else if (message.payload?.command === 'message') {
        toast.error('Message could not be sent. Please try again.', {timeout: 4000});
      } else {
        toast.error('Some conversations could not be opened.', {timeout: 4000});
      }
    } else if (message.command === 'mark_read') {
      const conversation = conversations.value.find((c) => c.id === message.payload.conversationId);
      message.payload.messageIds.forEach((id) => {
        const m = conversation.messages.find((m) => m.id === id);
        m.readOn = message.payload.readOn;
        m.readByParticipant = message.payload.readByParticipant;
        m.readByParticipantId = message.payload.participantId;
      });
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
    // the user left the page: no reconnect
    if (isLeaving) {
      return;
    }
    // the server rejected the token: retrying the same token can never
    // succeed, so surface it and stop the reconnect loop (a fresh page
    // load / re-login starts clean)
    if (ev && ev.code === WS_CLOSE_AUTH_FAILED) {
      showUnauthorizedWarning();
      return;
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

  // the socket may have been down while a conversation was created and its
  // push missed — one catch-up refetch per (re)connect (staff only)
  refreshConversations().catch((e) => {
    console.log('conversation catch-up failed', e);
  });
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

const websocketStatusInterval = setInterval(() => {
  websocketStatus.value = websocket?.readyState;
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
  // belt and braces for the onclose override below: never reconnect
  isLeaving = true;
  clearInterval(heartbeat);
  clearTimeout(retryTimeout);
  clearInterval(websocketStatusInterval);
  if (websocket) {
    websocket.onclose = async () => {};
    websocket.close();
    console.log('websocket closed');
  }
});

function mySide(conversation, message) {
  if (isUser) {
    return (
      message.sentByParticipantId !== conversation.initiatorParticipant?.id ||
      conversation.initiatorParticipant?.id === participantId.value
    );
  } else {
    return message.sentByParticipantId === participantId.value;
  }
}

function markRead(conversationId, messageIds) {
  sendWebsocketCommand('mark_read', {
    conversationId: conversationId,
    messageIds: messageIds,
    participantId: participantId.value,
    readOn: new Date(),
  });
}

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
              :my-side="mySide"
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
            :my-side="(message) => mySide(selectedConversation, message)"
            @mark-read="(messageIds) => markRead(selectedConversation.id, messageIds)"
          />
        </div>
      </div>

    </div>

</template>

<style scoped lang="scss">

</style>
