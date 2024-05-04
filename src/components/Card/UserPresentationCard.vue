<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';

export default {
  name: 'UserPresentationCard',
  components: {Card},
  data() {
    return {
      photoUrl: null,
    };
  },
  props: {
    presentationCardDetails: {
      type: Object,
      required: true,
    },
  },
  created() {
    requests.getPresentationCardPhoto(this.presentationCardDetails.id).then((response) => {
      this.photoUrl = window.URL.createObjectURL(new Blob([response.data]), {type: this.presentationCardDetails.photoContentType});
    });
  },
};
</script>

<template>
  <Card class="rounded-3xl p-4">
    <div class="grid grid-cols-12 gap-5 p-4">
      <div class="col-span-2">
        <img class="rounded-3xl h-[160px]" v-if="photoUrl !== null" :src="photoUrl" alt="Profile Photo"/>
      </div>
      <div class="col-span-10">
        <h3 class="text-slate-700 dark:text-slate-300">{{presentationCardDetails.name}}</h3>
        <p class="text-base text-slate-700 dark:text-slate-300">{{presentationCardDetails.bio}}</p>
      </div>
    </div>
  </Card>
</template>

<style scoped lang="scss">

</style>