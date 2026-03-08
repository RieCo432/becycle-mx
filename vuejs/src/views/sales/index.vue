<script>
import requests from '@/requests';
import {useToast} from 'vue-toastification';

// TODO: this needs to become a functional sales history

const toast = useToast();
export default {
  name: 'index',
  data() {
    return {
      saleHeaders: [],
    };
  },
  created() {
    requests.getSales().then((response) => {
      this.saleHeaders = response.data;
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12" v-for="saleHeader in saleHeaders" :key="saleHeader.id">
      <div class="grid grid-cols-3">
        <div class="col-span-1">
          <p>{{saleHeader.createdOn}}</p>
        </div>
        <div class="col-span-1">
          <p v-for="catalogueItemSaleLine in saleHeader.catalogueItemSaleLines" :key="catalogueItemSaleLine.id">
            {{catalogueItemSaleLine}}
          </p>
        </div>
        <div class="col-span-1">
          <p v-for="bikeSaleLine in saleHeader.bikeSaleLines" :key="bikeSaleLine.id">
            {{bikeSaleLine}}
          </p>
        </div>
      </div>
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>