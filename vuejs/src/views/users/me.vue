<script setup>
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import {ref} from 'vue';
import UserProfile from '@/views/users/UserProfile.vue';

const toast = useToast();


const username = ref('loading...');
const presentationCardDetails = ref(null);
const loadingPresentationCard = ref(true);

const photoUrl = ref('null');
const loadingPhoto = ref(true);

const loadingMyContracts = ref(true);
const myContracts = ref([]);

const loadingMyAccounts = ref(true);
const myAccounts = ref([]);

const loadingMyGroups = ref(true);
const myGroups = ref([]);

const loadingMyGroupAccounts = ref(true);
const myGroupAccounts = ref([]);

function updateMyCardDetails(name, bio, photo) {
  requests.postMyPresentationCardDetails(name, bio, photo).then((response) => {
    presentationCardDetails.value = response.data;
    toast.success('Card Updated!', {timeout: 2000});
    getPresentationCard();
  }).catch((error) => {
    toast.error(error.response.data.detail.description, {timeout: 2000});
  });
}

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

function deleteMyCard() {
  requests.deleteMyPresentationCard().then(() => {
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
requests.getUserMe().then((response) => {
  username.value = response.data.username;
});
function getPresentationCard() {
  requests.getMyPresentationCard().then((response) => {
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

requests.getMyGroups().then((response) => {
  myGroups.value = response.data;

  const getGroupAccountsPromises = myGroups.value.map((group) => requests.getGroupAccounts(group.id));

  Promise.all(getGroupAccountsPromises)
    .then((responses) => {
      responses.forEach((response) => {
        response.data.forEach((account) => {
          if (!myGroupAccounts.value.find((a) => a.id === account.id)) {
            myGroupAccounts.value.push(account);
          }
        });
      });
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    })
    .finally(() => {
      loadingMyGroupAccounts.value = false;
    });
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 2000});
}).finally(() => {
  loadingMyGroups.value = false;
});



requests.getMyAccounts().then((response) => {
  myAccounts.value = response.data;
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 2000});
}).finally(() => {
  loadingMyAccounts.value = false;
});

requests.getUserMyContracts().then((response) => {
  myContracts.value = response.data;
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 2000});
}).finally(() => {
  loadingMyContracts.value = false;
});


</script>

<template>
  <UserProfile
    :loading-presentation-card="loadingPresentationCard || loadingPhoto"
    :delete-card="deleteMyCard"
    :update-card-details="updateMyCardDetails"
    :presentation-card="presentationCardDetails"
    :photo-url="photoUrl"
    :user-accounts="myAccounts"
    :loading-user-accounts="loadingMyAccounts"
    :user-groups="myGroups"
    :loading-user-groups="loadingMyGroups"
    :group-accounts="myGroupAccounts"
    :loading-group-accounts="loadingMyGroupAccounts"
    :contracts="myContracts"
    :loading-contracts="loadingMyContracts"
  />
</template>

<style scoped lang="scss">

</style>
