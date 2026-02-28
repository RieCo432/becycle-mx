<script>
import BikeOverviewCard from '@/components/Card/BikeOverviewCard.vue';
import Button from '@/components/Button/index.vue';
import AddNewBikeCard from '@/components/Card/AddNewBikeCard.vue';

export default {
  name: 'BikeCatalogue',
  components: {AddNewBikeCard, BikeOverviewCard, Button},
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
  <div class="grid grid-cols-6 gap-5">
    <div class="col-span-1">
      <div class="grid grid-cols-1 gap-2">
        <div class="col-span-1">
          <AddNewBikeCard
            v-model="bikesFound"
            @updateSearch="handleSearchUpdate"
            @bike-added="handleBikeAdded"
          />
        </div>
      </div>
    </div>
    <div class="col-span-5 row-span-3 gap-2 h-[84vh] overflow-auto">
      <div class="overscroll-contain">
        <div class="grid grid-cols-5 gap-2">
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
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>