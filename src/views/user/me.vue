<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="lg:col-span-8 col-span-12">
      <Card :title="username">
        <p></p>
      </Card>
    </div>
  </div>

</template>

<script>

import Card from '@/components/Card/index.vue';
import requests from '@/requests';

export default {
  components: {
    Card,
  },
  data() {
    return {
      username: 'loading...',
    };
  },
  mounted() {
    requests.getUserMe().then((response) => {
      console.log(response.data);
      this.username = response.data.username;
    });
  },
};


</script>


<style scoped lang="scss">

</style>
