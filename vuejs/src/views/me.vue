<script setup>
import {useCredentialsStore} from '@/store/credentialsStore';
import ClientMe from '@/views/client/me.vue';
import UserMe from '@/views/user/me.vue';
import {ref} from 'vue';

const credentialsStore = useCredentialsStore();

const tokenType = ref(credentialsStore.getTokenType());

</script>

<template>
  <div>
    <ClientMe v-if="tokenType === 'client'"></ClientMe>
    <UserMe v-else-if="tokenType === 'user'"></UserMe>
  </div>
</template>

<style scoped lang="scss">

</style>
