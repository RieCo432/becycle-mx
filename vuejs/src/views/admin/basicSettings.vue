<script>
import UpdateAddressCard from '@/components/Card/UpdateAddressCard.vue';
import ManageContractTypesCard from '@/components/Card/ManageContractTypesCard.vue';
import ManageExpenseTypesCard from '@/components/Card/ManageExpenseTypesCard.vue';

export default {
  name: 'basicSettings',
  components: {ManageExpenseTypesCard, ManageContractTypesCard, UpdateAddressCard},
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-6">
      <UpdateAddressCard></UpdateAddressCard>
    </div>
    <div class="col-span-6 row-span-2">
      <ManageExpenseTypesCard></ManageExpenseTypesCard>
    </div>
    <div class="col-span-6">
      <ManageContractTypesCard></ManageContractTypesCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
