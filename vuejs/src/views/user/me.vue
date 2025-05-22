<template>
  <div class="grid lg:grid-cols-12 grid-cols-6 gap-5">
    <div class="col-span-6">
      <UserPresentationCard
          v-if="!loadingPresentationCard"
          :presentation-card-details="presentationCardDetails"
          editable
          :update-card-details="updateMyCardDetails"
          :delete-card="deleteMyCard"
      />
    </div>
  </div>
</template>

<script>
import requests from '@/requests';
import UserPresentationCard from '@/components/Card/UserPresentationCard.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'UserMe',
  components: {
    UserPresentationCard,
  },
  data() {
    return {
      username: 'loading...',
      presentationCardDetails: null,
      photoUrl: null,
      loadingPresentationCard: true,
    };
  },
  methods: {
    updateMyCardDetails(name, bio, photo) {
      requests.postMyPresentationCardDetails(name, bio, photo).then((response) => {
        this.presentationCardDetails = response.data;
        toast.success('Card Updated!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    deleteMyCard() {
      requests.deleteMyPresentationCard().then(() => {
        this.presentationCardDetails = {
          name: 'NOT SET',
          bio: 'NOT SET',
          id: 'NOTSET',
          photoContentType: 'image/jpeg',
        };
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
  },
  created() {
    requests.getUserMe().then((response) => {
      this.username = response.data.username;
    });
    requests.getMyPresentationCard().then((response) => {
      this.presentationCardDetails = response.data;
    }).catch((error) => {
      if (error.status !== 404) {
      }
      this.presentationCardDetails = {
        name: 'NOT SET',
        bio: 'NOT SET',
        id: 'NOTSET',
        photoContentType: 'image/jpeg',
      };
    }).finally(() => {
      this.loadingPresentationCard = false;
    });
  },
};


</script>


<style scoped lang="scss">

</style>
