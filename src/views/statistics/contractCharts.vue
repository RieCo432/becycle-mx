<script>
import 'vue-slider-component/theme/antd.css';
import TotalContractsDateSeriesCard from '@/components/Card/TotalContractsDateSeriesCard.vue';
import ActiveContractsDateSeriesCard from '@/components/Card/ActiveContractsDateSeriesCard.vue';
import NewContractsDateSeriesCard from '@/components/Card/NewContractsDateSeriesCard.vue';
import ReturnedContractsDateSeriesCard from '@/components/Card/ReturnedContractsDateSeriesCard.vue';
export default {
  name: 'contractCharts',
  components: {
    ReturnedContractsDateSeriesCard,
    NewContractsDateSeriesCard,
    ActiveContractsDateSeriesCard,
    TotalContractsDateSeriesCard,
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-6">
      <TotalContractsDateSeriesCard></TotalContractsDateSeriesCard>
    </div>
    <div class="col-span-6">
      <ActiveContractsDateSeriesCard></ActiveContractsDateSeriesCard>
    </div>
    <div class="col-span-6">
      <NewContractsDateSeriesCard></NewContractsDateSeriesCard>
    </div>
    <div class="col-span-6">
      <ReturnedContractsDateSeriesCard></ReturnedContractsDateSeriesCard>
    </div>
  </div>

</template>

<style lang="scss">
</style>
