<script>
import requests from '@/requests';
import CatalogueItemCard from '@/components/Card/CatalogueItemCard.vue';
import AddNewCatalogueItemCard from '@/components/Card/AddNewCatalogueItemCard.vue';
import Card from '@/components/Card/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import Checkbox from '@/components/Checkbox';
import {distance} from 'fastest-levenshtein';

export default {
  name: 'catalogue',
  components: {Card, AddNewCatalogueItemCard, CatalogueItemCard, TextInput, Checkbox},
  data() {
    return {
      catalogueItems: [],
      searchQuery: '',
      includeSecondHand: true,
      includeNew: true,
      includeAvailable: true,
      includeUnavailable: true,
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
    sortedAndFileteredCatalogueItems() {
      return this.catalogueItems
        .filter((item) => {
          return (
            (this.searchQuery === '' ||
              item.name.toLowerCase().startsWith(this.searchQuery.toLowerCase()) ||
              item.description.toLowerCase().startsWith(this.searchQuery.toLowerCase()) ||
              distance(this.searchQuery, item.name) <= 3 ||
              distance(this.searchQuery, item.description) <= 3
            ) &&
            (this.includeSecondHand || !item.isSecondHand) &&
            (this.includeNew || item.isSecondHand) &&
            (this.includeAvailable || !item.available) &&
            (this.includeUnavailable || item.available)
          );
        })
        .sort((a, b) => (a.available ? -1 : 1) - (b.available ? -1 : 1));
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-6 xl:grid-cols-8 gap-5">
    <div class="col-span-1">
      <Card title="Search Catalogue" class="dark:text-slate-300 text-slate-700">
        <div class="grid grid-cols-1 gap-2">
          <div class="col">
            <TextInput
              label="Search Catalogue"
              v-model="searchQuery"
            />
          </div>
          <div class="col">
            <Checkbox
            label="Include Second Hand"
            v-model="includeSecondHand"
            activeClass="ring-primary-500 bg-primary-500"
            />
          </div>
          <div class="col">
            <Checkbox
            label="Include New"
            v-model="includeNew"
            activeClass="ring-primary-500 bg-primary-500"
            />
          </div>
          <div class="col">
            <Checkbox
            label="Include Available"
            v-model="includeAvailable"
            activeClass="ring-primary-500 bg-primary-500"
            />
          </div>
          <div class="col">
            <Checkbox
            label="Include Unavailable"
            v-model="includeUnavailable"
            activeClass="ring-primary-500 bg-primary-500"
            />
          </div>
        </div>
      </Card>
    </div>
    <div class="col-span-1">
      <AddNewCatalogueItemCard
        @catalogue-item-added="addItemToCatalogue"
      ></AddNewCatalogueItemCard>
    </div>
    <div class="col-span-1" v-for="item in sortedAndFileteredCatalogueItems" :key="item.id">
      <CatalogueItemCard editable :item-details="item" @catalogueItemUpdated="updateCatalogueItem"/>
    </div>

  </div>
</template>

<style scoped lang="scss">

</style>