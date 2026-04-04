<script>
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import SaleSummaryCard from '@/components/Card/SaleSummaryCard.vue';

const toast = useToast();
export default {
  name: 'index',
  components: {SaleSummaryCard},
  data() {
    return {
      saleHeaders: [],
    };
  },
  created() {
    requests.getSales(false, true).then((response) => {
      this.saleHeaders = response.data.sort((a, b) => new Date(b.transactionHeader.postedOn) - new Date(a.transactionHeader.postedOn));
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12" v-for="saleHeader in saleHeaders" :key="saleHeader.id">
      <SaleSummaryCard
        :sale-header="saleHeader"/>
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>