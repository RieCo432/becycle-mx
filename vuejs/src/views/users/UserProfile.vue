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
    required: false,
  },
  updateCardDetails: {
    type: Function,
    required: false,
  },
  deleteCard: {
    type: Function,
    required: false,
  },
  loadingPresentationCard: {
    type: Boolean,
    required: false,
  },
  userAccounts: {
    type: Array,
    required: false,
  },
  loadingUserAccounts: {
    type: Boolean,
    required: false,
  },
  userGroups: {
    type: Array,
    required: false,
  },
  loadingUserGroups: {
    type: Boolean,
    required: false,
  },
  groupAccounts: {
    type: Array,
    required: false,
  },
  loadingGroupAccounts: {
    type: Boolean,
    required: false,
  },
  contracts: {
    type: Array,
    required: false,
  },
  loadingContracts: {
    type: Boolean,
    required: false,
  },
  photoUrl: {
    type: String,
    required: false,
  },
  user: {
    type: Object,
    required: false,
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
        :user="user"
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