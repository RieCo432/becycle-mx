<script setup>
import UserPresentationCard from '@/components/Card/UserPresentationCard.vue';
import {defineProps} from 'vue';
import Card from '@/components/Card/index.vue';
import TableSkeleton from '@/components/Skeleton/TableSkeleton.vue';
import GroupsCard from '@/components/Card/GroupsCard.vue';
import UserContractsCard from '@/components/Card/UserContractsCard.vue';
import AccountsCard from '@/components/Card/AccountsCard.vue';

const props = defineProps({
  presentationCard: {
    type: Object,
    required: true,
  },
  updateCardDetails: {
    type: Function,
    required: true,
  },
  deleteCard: {
    type: Function,
    required: true,
  },
  loadingPresentationCard: {
    type: Boolean,
    required: true,
  },
  userAccounts: {
    type: Array,
    required: true,
  },
  loadingUserAccounts: {
    type: Boolean,
    required: true,
  },
  userGroups: {
    type: Array,
    required: true,
  },
  loadingUserGroups: {
    type: Boolean,
    required: true,
  },
  groupAccounts: {
    type: Array,
    required: true,
  },
  loadingGroupAccounts: {
    type: Boolean,
    required: true,
  },
  contracts: {
    type: Array,
    required: true,
  },
  loadingContracts: {
    type: Boolean,
    required: true,
  },
  photoUrl: {
    type: String,
    required: true,
  },
});



</script>

<template>
  <div class="grid lg:grid-cols-12 grid-cols-6 gap-5">
    <div class="col-span-6">
      <UserPresentationCard
        :loading="loadingPresentationCard"
        :presentation-card-details="presentationCard"
        editable
        :update-item-details="updateCardDetails"
        :delete-card="deleteCard"
        :photo-url="photoUrl"
      />
    </div>
    <div class="col-span-6">
      <AccountsCard
        title="User Accounts"
        :accounts="userAccounts"
        :loading="loadingUserAccounts"
      />
    </div>
    <div class="col-span-12">
      <UserContractsCard
        :loading="loadingContracts"
        :contracts="contracts"
      />
    </div>
    <div class="col-span-6">
      <GroupsCard
        :loading="loadingUserGroups"
        :groups="userGroups"
      />
    </div>
    <div class="col-span-6">
      <AccountsCard
        title="Group Accounts"
        :accounts="groupAccounts"
        :loading="loadingGroupAccounts"
      />
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>