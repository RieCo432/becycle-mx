<script>
import requests from '@/requests';
import UserPresentationCard from '@/components/Card/UserPresentationCard.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'ourVolunteers',
  components: {UserPresentationCard},
  data() {
    return {
      allUserPresentationCardDetails: [],
      isUserAdmin: false,
    };
  },
  created() {
    requests.getPublicUserPresentationCards().then((response) => {
      this.allUserPresentationCardDetails = response.data;
    });
    requests.getUserMeNo401Redirect().then((response) => {
      this.isUserAdmin = response.data.admin;
    });
  },
  methods: {
    updateUserPresentationCard(presentationCardId, name, bio, photo) {
      requests.postUserPresentationCardDetails(presentationCardId, name, bio, photo).then((response) => {
        const indexInArray = this.allUserPresentationCardDetails.findIndex((c) => c.id === response.data.id);
        this.allUserPresentationCardDetails.splice(indexInArray, 1, response.data);
        toast.success('Card Updated!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    deleteUserPresentationCard(presentationCardId) {
      requests.deleteUserPresentationCardDetails(presentationCardId).then((response) => {
        const indexInArray = this.allUserPresentationCardDetails.findIndex((c) => c.id === response.data.id);
        this.allUserPresentationCardDetails.splice(indexInArray, 1);
        toast.success('Card Deleted!', {timeout: 2000});
      });
    },
  },
};
</script>

<template>
  <div class="grid 2xl:grid-cols-2 grid-cols-1 gap-5">
    <div v-for="userPresentationCardDetails in allUserPresentationCardDetails" class="col-span-1"
         :key="userPresentationCardDetails.id">
      <UserPresentationCard
          :key="userPresentationCardDetails.id"
          :editable="isUserAdmin"
          :update-card-details="(name, bio, photo) => updateUserPresentationCard(userPresentationCardDetails.id, name, bio, photo)"
          :presentation-card-details="userPresentationCardDetails"
          :delete-card="() => deleteUserPresentationCard(userPresentationCardDetails.id)"
      ></UserPresentationCard>
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>
