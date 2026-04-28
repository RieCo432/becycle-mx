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
  props: {
    bikeClickAction: {
      type: Function,
      default: null,
    },
    includeRental: {
      type: Boolean,
      default: true,
    },
    includeSale: {
      type: Boolean,
      default: true,
    },
    outerGridColClasses: {
      type: String,
      default: 'grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5',
    },
    innerGridColSpanClasses: {
      type: String,
      default: 'col-span-1 lg:col-span-2 xl:col-span-3 2xl:col-span-4',
    },
    innerGridColClasses: {
      type: String,
      default: 'grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4',
    },
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
  <div :class="`grid ${outerGridColClasses} gap-5 w-full`">
    <div class="col-span-1 lg:sticky lg:top-0">
      <div class="grid grid-cols-1 gap-2">
        <div class="col-span-1">
          <AddNewBikeCard
            v-model="bikesFound"
            :include-rental-initial="includeRental"
            :include-sale-initial="includeSale"
            @updateSearch="handleSearchUpdate"
            @bike-added="handleBikeAdded"
          />
        </div>
      </div>
    </div>
    <div :class="`${innerGridColSpanClasses} row-span-3 gap-2`">
      <div :class="`grid ${innerGridColClasses} gap-2`">
        <div class="col-span-1" v-for="bike in bikesFound" :key="bike.id">
          <BikeOverviewCard
            no-title
            :bike="bike"
            :bike-search="bikeSearch"
          >
            <template #footer>
              <div :class="`w-full grid grid-cols-${$slots.specialAction ? 2 : 1} gap-2`">
                <Button class="col" @click="viewBike(bike.id)">Go to Bike</Button>
                <slot name="specialAction" :bike="bike"/>
              </div>
            </template>
          </BikeOverviewCard>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>