<script>
import BikeSearchCard from '@/components/Card/BikeSearchCard.vue';
import BikeOverviewCard from '@/components/Card/BikeOverviewCard.vue';
import Button from '@/components/Button/index.vue';
import AddNewBikeCard from '@/components/Card/AddNewBikeCard.vue';

export default {
  name: 'BikeCatalogue',
  components: {AddNewBikeCard, BikeOverviewCard, BikeSearchCard, Button},
  data() {
    return {
      bikesFound: [],
      bikeSearch: {},
    };
  },
  methods: {
    handleSearchUpdate(search) {
      this.bikeSearch = search;
    },
    viewBike(bikeId) {
      const routeData = this.$router.resolve({path: `/bikes/${bikeId}`});
      window.open(routeData.href, '_blank');
    },
    handleBikeAdded(bike) {
      this.bikesFound.push(bike);
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-6 gap-2">
    <div class="col-span-1 row-span-2">
      <BikeSearchCard
        v-model="bikesFound"
        @updateSearch="handleSearchUpdate"
      />
    </div>
    <div class="col-span-1 row-span-2">
      <AddNewBikeCard
        @bike-added="handleBikeAdded"
      />
    </div>
    <div class="col-span-1" v-for="bike in bikesFound" :key="bike.id">
      <BikeOverviewCard
        no-title
        :bike="bike"
        :bike-search="bikeSearch"
      >
        <template #footer>
          <Button class="w-full" @click="viewBike(bike.id)">Go to Bike</Button>
        </template>
      </BikeOverviewCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>