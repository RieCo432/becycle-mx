<script>
import UpdateAddressCard from '@/components/Card/UpdateAddressCard.vue';
import ManageContractTypesCard from '@/components/Card/ManageContractTypesCard.vue';
import ManageFaqCard from '@/components/Card/ManageFaqCard.vue';

export default {
  name: 'basicSettings',
  components: {ManageFaqCard, ManageContractTypesCard, UpdateAddressCard},
};
</script>

<template>
  <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">
    <div class="col-span-6">
      <UpdateAddressCard></UpdateAddressCard>
    </div>
    <div class="col-span-6">
      <ManageContractTypesCard></ManageContractTypesCard>
    </div>
    <div class="col-span-6 xl:col-span-12">
      <ManageFaqCard></ManageFaqCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
