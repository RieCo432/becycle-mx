<script setup>
import UserPresentationCard from '@/components/Card/UserPresentationCard.vue';
import {defineProps, ref} from 'vue';
import GroupsCard from '@/components/Card/GroupsCard.vue';
import UserContractsCard from '@/components/Card/UserContractsCard.vue';
import AccountsCard from '@/components/Card/AccountsCard.vue';
import requests from '@/requests';

const props = defineProps({
  getUserPresentationCard: {
    type: Function,
    required: true,
  },

  getUserAccounts: {
    type: Function,
    required: true,
  },

  getUserGroups: {
    type: Function,
    required: true,
  },

  getUserContracts: {
    type: Function,
    required: true,
  },

  getUser: {
    type: Function,
    required: true,
  },
  updateCardDetails: {
    type: Function,
    required: false,
  },
  deleteCard: {
    type: Function,
    required: false,
  },
  canEditCard: {
    type: Boolean,
    required: false,
  },
});

const user = ref(null);
const presentationCardDetails = ref(null);
const loadingPresentationCard = ref(true);

const photoUrl = ref('null');
const loadingPhoto = ref(true);

const loadingContracts = ref(true);
const contracts = ref([]);

const loadingAccounts = ref(true);
const accounts = ref([]);

const loadingGroups = ref(true);
const groups = ref([]);

const loadingGroupAccounts = ref(true);
const groupAccounts = ref([]);


function getImage() {
  if (presentationCardDetails.value.id !== 'NOTSET') {
    requests.getPresentationCardPhoto(presentationCardDetails.value.id).then((response) => {
      const photoFile = new File([response.data], {type: presentationCardDetails.value.photoContentType});
      photoUrl.value = window.URL.createObjectURL(photoFile);
    })
      .catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      })
      .finally(() => {
        loadingPhoto.value = false;
      });
  }
}


props.getUser().then((response) => {
  user.value = response.data;
});

function getPresentationCard() {
  props.getUserPresentationCard().then((response) => {
    presentationCardDetails.value = response.data;
    getImage();
  }).catch((error) => {
    if (error.status !== 404) {
    }
    presentationCardDetails.value = {
      name: 'NOT SET',
      bio: 'NOT SET',
      id: 'NOTSET',
      photoContentType: 'image/jpeg',
    };
    photoUrl.value = null;
    loadingPhoto.value = false;
  }).finally(() => {
    loadingPresentationCard.value = false;
  });
}

getPresentationCard();


props.getUserGroups().then((response) => {
  groups.value = response.data;

  const getGroupAccountsPromises = groups.value.map((group) => requests.getGroupAccounts(group.id));

  Promise.all(getGroupAccountsPromises)
    .then((responses) => {
      responses.forEach((response) => {
        response.data.forEach((account) => {
          if (!groupAccounts.value.find((a) => a.id === account.id)) {
            groupAccounts.value.push(account);
          }
        });
      });
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    })
    .finally(() => {
      loadingGroupAccounts.value = false;
    });
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 2000});
}).finally(() => {
  loadingGroups.value = false;
});

props.getUserAccounts().then((response) => {
  accounts.value = response.data;
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 2000});
}).finally(() => {
  loadingAccounts.value = false;
});

props.getUserContracts().then((response) => {
  contracts.value = response.data;
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 2000});
}).finally(() => {
  loadingContracts.value = false;
});

function updateCardDetailsWrapped(details) {
  props.updateCardDetails(details).then((response) => {
    presentationCardDetails.value = response.data;
    getPresentationCard();
    toast.success('Card Updated!', {timeout: 2000});
  }).catch((error) => {
    toast.error(error.response.data.detail.description, {timeout: 2000});
  });
}

function deleteCardWrapped() {
  props.deleteCard().then(() => {
    presentationCardDetails.value = {
      name: 'NOT SET',
      bio: 'NOT SET',
      id: 'NOTSET',
      photoContentType: 'image/jpeg',
    };
    photoUrl.value = null;
  }).catch((error) => {
    toast.error(error.response.data.detail.description, {timeout: 2000});
  });
}

</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-full xl:col-span-6">
      <UserPresentationCard
        :loading="loadingPresentationCard || loadingPhoto"
        :presentation-card-details="presentationCardDetails"
        :editable="canEditCard"
        :update-item-details="updateCardDetailsWrapped"
        :delete-card="deleteCardWrapped"
        :photo-url="photoUrl"
      />
    </div>
    <div class="col-span-full xl:col-span-6">
      <AccountsCard
        title="User Accounts"
        :accounts="accounts"
        :loading="loadingAccounts"
        columns="2"
      />
    </div>
    <div class="col-span-full">
      <UserContractsCard
        :loading="loadingContracts"
        :contracts="contracts"
        :user="user"
      />
    </div>
    <div class="col-span-full xl:col-span-3">
      <GroupsCard
        :loading="loadingGroups"
        :groups="groups"
      />
    </div>
    <div class="col-span-full xl:col-span-9">
      <AccountsCard
        title="Group Accounts"
        :accounts="groupAccounts"
        :loading="loadingGroupAccounts"
        columns="3"
      />
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>
