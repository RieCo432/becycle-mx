<script setup>
import {useCredentialsStore} from '@/store/credentialsStore';
import Conversation from '@/views/chat/Conversation.vue';
import ConversationPicker from '@/views/chat/ConversationPicker.vue';
import {computed, reactive, ref, watch} from 'vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';

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

const websocket = new WebSocket('ws://localhost:8000/chats/ws');

const websocketStatus = ref(0);

websocket.onopen = async (ev) => {
  console.log('websocket opened');
  websocket.send(JSON.stringify({
    token: credentialStore.token,
  }));
  websocketStatus.value = websocket.readyState;

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
  websocketStatus.value = websocket.readyState;
  const message = JSON.parse(d.data);
  console.log({message, myConversation: myConversation.value});

  conversations.value.forEach((c) => {
    if (c.id === message.conversationId) {
      c.messages.push(message);
    }
  });
};

websocket.onclose = (ev) => {
  console.log('websocket closed');
  websocketStatus.value = websocket.readyState;
};

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


</script>

<template>
    <div class="grid grid-cols-12 gap-5">
      <div class="col-span-full">
        <span>{{websocketStatus}}</span>
      </div>
      <template v-if="isUser">
        <div class="col-span-3">
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
        :class="`col-span-${isUser ? 9 : 12}`">
        <Conversation
          :conversation="selectedConversation"
          :participantId="participantId"
          @send-message="sendMessage"
        />
      </div>
    </div>

</template>

<style scoped lang="scss">

</style>
