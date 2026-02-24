<script>
import requests from '@/requests';
import CatalogueItemCard from '@/components/Card/CatalogueItemCard.vue';
import AddNewCatalogueItemCard from '@/components/Card/AddNewCatalogueItemCard.vue';

export default {
  name: 'catalogue',
  components: {AddNewCatalogueItemCard, CatalogueItemCard},
  data() {
    return {
      catalogueItems: [],
    };
  },
  methods: {
    addItemToCatalogue(item) {
      this.catalogueItems.push(item);
    },
    updateCatalogueItem(item) {
      const indexInArray = this.catalogueItems.findIndex((i) => (i.id === item.id));
      this.catalogueItems.splice(indexInArray, 1, item);
    },
  },
  created() {
    requests.getItemCatalogue(true).then((response) => {
      this.catalogueItems = response.data;
    });
  },
  computed: {
    sortedCatalogueItems() {
      return this.catalogueItems.toSorted((a, b) => (a.available ? -1 : 1) - (b.available ? -1 : 1));
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-6 xl:grid-cols-12 gap-5">
    <div class="col-span-2" v-for="item in sortedCatalogueItems" :key="item.id">
      <CatalogueItemCard editable :item-details="item" @catalogueItemUpdated="updateCatalogueItem"/>
    </div>
    <div class="col-span-2">
      <AddNewCatalogueItemCard
        @catalogue-item-added="addItemToCatalogue"
      ></AddNewCatalogueItemCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>