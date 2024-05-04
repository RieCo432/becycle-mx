<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-6">
      <UserPresentationCard
          v-if="!loadingPresentationCard"
          :presentation-card-details="presentationCardDetails"
          editable
          :update-card-details="updateMyCardDetails"
      />
    </div>
  </div>
</template>

<script>

import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import UserPresentationCard from '@/components/Card/UserPresentationCard.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'UserMe',
  components: {
    UserPresentationCard,
    Card,
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
      });
    },
  },
  created() {
    requests.getUserMe().then((response) => {
      this.username = response.data.username;
    });
    requests.getMyPresentationCard().then((response) => {
      this.presentationCardDetails = response.data;
      this.loadingPresentationCard = false;
    });
  },
};


</script>


<style scoped lang="scss">

</style>
