<script lang="ts">
import {defineComponent} from 'vue';
import ManageUserGroupsCard from '@/components/Card/ManageUserGroupsCard.vue';
import requests from '@/requests';

export default defineComponent({
  name: 'userGroups',
  components: {ManageUserGroupsCard},
  data() {
    return {
      user: null,
    };
  },
  mounted() {
    requests.getUserMe().then((response) => {
      this.user = response.data;
    });
  },
});
</script>

<template>
  <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">
    <div class="col-span-6">
      <ManageUserGroupsCard v-if="user" :user="user"></ManageUserGroupsCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
