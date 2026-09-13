<script setup>
import requests from '@/requests';
import UserProfile from '@/views/users/UserProfile.vue';

</script>

<template>
  <UserProfile
    :get-user="requests.getUserMe"
    :get-user-accounts="requests.getMyAccounts"
    :get-user-contracts="requests.getUserMyContracts"
    :get-user-groups="requests.getMyGroups"
    :get-user-presentation-card="requests.getMyPresentationCard"
    :delete-card="requests.deleteMyPresentationCard"
    :update-card-details="requests.postMyPresentationCardDetails"
  />
</template>

<style scoped lang="scss">

</style>
