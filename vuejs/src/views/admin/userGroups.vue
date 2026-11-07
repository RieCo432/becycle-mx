<script lang="ts">
import {defineComponent} from 'vue';
import ManageUserGroupsCard from '@/components/Card/ManageUserGroupsCard.vue';

export default defineComponent({
  name: 'userGroups',
  components: {ManageUserGroupsCard},
});
</script>

<template>
  <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">
    <div class="col-span-6">
      <ManageUserGroupsCard></ManageUserGroupsCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
