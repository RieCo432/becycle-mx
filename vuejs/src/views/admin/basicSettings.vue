<script>
import UpdateAddressCard from '@/components/Card/UpdateAddressCard.vue';
import ManageContractTypesCard from '@/components/Card/ManageContractTypesCard.vue';
import ManageExpenseTypesCard from '@/components/Card/ManageExpenseTypesCard.vue';
import ManageExpenseTagsCard from '@/components/Card/ManageExpenseTagsCard.vue';
import ManageFaqCard from '@/components/Card/ManageFaqCard.vue';
import requests from '@/requests';

export default {
  name: 'basicSettings',
  components: {ManageFaqCard, ManageExpenseTypesCard, ManageContractTypesCard, UpdateAddressCard, ManageExpenseTagsCard},
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
};
</script>

<template>
  <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">
    <div class="col-span-6">
      <UpdateAddressCard v-if="user" :user="user"></UpdateAddressCard>
    </div>
    <div class="col-span-6">
      <ManageExpenseTypesCard v-if="user" :user="user"></ManageExpenseTypesCard>
    </div>
    <div class="col-span-6">
      <ManageContractTypesCard v-if="user" :user="user"></ManageContractTypesCard>
    </div>
    <div class="col-span-6">
      <ManageExpenseTagsCard v-if="user" :user="user"></ManageExpenseTagsCard>
    </div>
    <div class="col-span-6 xl:col-span-12">
      <ManageFaqCard v-if="user" :user="user"></ManageFaqCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
