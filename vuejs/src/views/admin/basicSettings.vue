<script>
import UpdateAddressCard from '@/components/Card/UpdateAddressCard.vue';
import ManageContractTypesCard from '@/components/Card/ManageContractTypesCard.vue';
import ManageExpenseTypesCard from '@/components/Card/ManageExpenseTypesCard.vue';
import ManageExpenseTagsCard from "@/components/Card/ManageExpenseTagsCard.vue";

export default {
  name: 'basicSettings',
  components: {ManageExpenseTypesCard, ManageContractTypesCard, UpdateAddressCard, ManageExpenseTagsCard},
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-6">
      <UpdateAddressCard></UpdateAddressCard>
    </div>
    <div class="col-span-6">
      <ManageExpenseTypesCard></ManageExpenseTypesCard>
    </div>
    <div class="col-span-6">
      <ManageContractTypesCard></ManageContractTypesCard>
    </div>
    <div class="col-span-6">
      <ManageExpenseTagsCard></ManageExpenseTagsCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
