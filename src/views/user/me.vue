<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <UserPresentationCard v-if="!loadingPresentationCard" :presentation-card-details="presentationCardDetails"/>
    </div>
  </div>
</template>

<script>

import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import UserPresentationCard from '@/components/Card/UserPresentationCard.vue';

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
