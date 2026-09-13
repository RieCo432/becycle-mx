<script setup>
import requests from '@/requests';
import UserProfile from '@/views/users/UserProfile.vue';
import {useRoute} from 'vue-router';

const route = useRoute();
const userId = route.params.userId;

</script>

<template>
  <UserProfile
    :get-user="() => requests.getUser(userId)"
    :get-user-accounts="() => requests.getUserAccounts(userId)"
    :get-user-contracts="() => requests.getUserContracts(userId)"
    :get-user-groups="() => requests.getUserGroups(userId)"
    :get-user-presentation-card="() => requests.getUserPresentationCard(userId)"/>
<!--    :delete-card="requests.deleteUser"-->
<!--    :update-card-details="requests.postMyPresentationCardDetails"-->
</template>

<style scoped lang="scss">

</style>