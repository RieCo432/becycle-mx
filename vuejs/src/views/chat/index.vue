<script setup>
import Card from '@/components/Card';
import Icon from '@/components/Icon';
import window from '@/mixins/window';

import {useCredentialsStore} from '@/store/credentialsStore';
import Conversation from '@/views/chat/Conversation.vue';
import ConversationPicker from '@/views/chat/ConversationPicker.vue';
import {ref} from 'vue';
import requests from '@/requests';

const credentialStore = useCredentialsStore();

const isUser = credentialStore.tokenType === 'user';

const selectedConversation = ref(null);
const participantId = ref(null);


function selectConversation(conversation) {
  selectedConversation.value = conversation;
}


requests.getMyConversation().then((response) => {
  selectConversation(response.data);
});

requests.getParticipantMe().then((response) => {
  participantId.value = response.data.id;
});


</script>

<template>
    <div class="grid grid-cols-12 gap-5">
      <template v-if="isUser">
        <div class="col-span-3">
          <ConversationPicker
            :selectedConversation="selectedConversation"
            @conversation-selected="selectConversation"
          />
        </div>
      </template>
      <div
        v-if="selectedConversation"
        :class="`col-span-${isUser ? 9 : 12}`">
        <Conversation
          :conversation="selectedConversation"
          :participantId="participantId"
        />
      </div>
    </div>

</template>

<style scoped lang="scss">

</style>
