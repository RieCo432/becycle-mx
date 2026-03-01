<script>
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Card from '@/components/Card/index.vue';
import Button from '@/components/Button/index.vue';
import CatalogueItemCard from '@/components/Card/CatalogueItemCard.vue';
import TextInput from '@/components/TextInput/index.vue';
import Modal from '@/components/Modal/Modal.vue';

const toast = useToast();
export default {
  name: 'PointOfSale',
  components: {Modal, TextInput, CatalogueItemCard, Card, Button},
  data() {
    return {
      openSales: [],
      currentSale: null,
      showCatalogueBrowseModal: false,
      showBikeBrowseModal: false,
      catalogueItems: [],
      showItems: false,
      showBikes: false,
      showUsed: null,
      showQuantityModal: false,
      selectedItem: null,
      quantity: 0,
    };
  },
  created() {
    requests.getSales(true).then((response) => {
      this.openSales = response.data;
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });
    requests.getItemCatalogue(false).then((response) => {
      this.catalogueItems = response.data;
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });
  },
  methods: {
    startNewSale() {
      requests.postNewSale().then((response) => {
        this.currentSale = response.data;
        this.openSales.push(this.currentSale);
        toast.success('Sale Started!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    continueSale(saleId) {
      this.currentSale = this.openSales.find((sale) => sale.id === saleId);
      toast.success('Sale Continued!', {timeout: 2000});
    },
    addItemToSale() {
      const catalogueItemSaleLine = {
        saleHeaderId: this.currentSale.id,
        catalogueItemId: this.selectedItem.id,
        quantity: this.quantity,
        salePrice: this.selectedItem.recommendedRetailPrice * this.quantity,
      };
      requests.postCatalogueItemSaleLine(catalogueItemSaleLine).then((response) => {
        toast.success('Item added to sale!', {timeout: 2000});
        this.currentSale.catalogueItemSaleLines.push(response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
      this.showQuantityModal = false;
    },
    selectItem(item) {
      this.selectedItem = item;
      this.quantity = 0;
      console.log('Selected item:', this.selectedItem);
      this.showQuantityModal = true;
    },
    closeQuantityModal() {
      this.showQuantityModal = false;
      this.selectedItem = null;
      this.quantity = 0;
    },
  },
  computed: {
    totalSalePrice() {
      return this.currentSale.catalogueItemSaleLines.reduce((total, line) => total + line.salePrice, 0) +
        this.currentSale.bikeSaleLines.reduce((total, line) => total + line.salePrice, 0);
    },
  },
};
</script>

<template>
  <Card title="Point of Sale">
    <div v-if="currentSale === null">
      <h2>Start New Sale</h2>
      <Button text="New Sale" @click="startNewSale"></Button>
      <h2>Open Sales</h2>
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-4" v-for="sale in openSales" :key="sale.id">
          {{ sale }}
          <Button text="Continue Sale" @click="continueSale(sale.id)"></Button>
        </div>
      </div>
    </div>
    <div v-else>
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-12">
          <Button class="w-full" text="Close Sale" @click="currentSale = null"></Button>
        </div>
        <div class="col-span-12">
          <h2>Sale: {{ currentSale.id }}</h2>
        </div>
        <div class="col-span-8">
          
          <template v-if="showItems">
            <div v-if="showUsed === null" class="grid grid-cols-2 gap-5">
              <div class="col-span-full">
                <Button text="Back" @click="() => {showBikes = null; showItems = null}" class="w-full"/>
              </div>
              <div class="col-span-1">
                <Button text="New" @click="showUsed = false" class="w-full"/>
              </div>
              <div class="col-span-1">
                <Button text="Used" @click="showUsed = true" class="w-full"/>
              </div>
            </div>
            <div v-else class="grid grid-cols-5 gap-5">
              <div class="col-span-5">
                <Button text="Back" @click="showUsed = null" class="w-full"/>
              </div>
              <div v-for="item in catalogueItems.filter((item) => item.isSecondHand === showUsed)" :key="item.id"
                   class="col-span-1" @click="() => selectItem(item)">
                <CatalogueItemCard :item-details="item"/>
              </div>
            </div>
          </template>

          <template v-else-if="showBikes">
            <Button text="Back" @click="() => {showBikes = null; showItems = null}" class="w-full"/>
          </template>

          <template v-else>
            <div class="grid grid-cols-2 gap-5">
              <div class="col-span-1">
                <Button class="w-full h-full" text="Add Catalogue Item" @click="() => showItems = true"></Button>
              </div>
              <div class="col-span-1">
                <Button class="w-full h-full" text="Add Bike" @click="() => showBikes = true"></Button>
              </div>
            </div>
          </template>
        </div>
        <div class="col-span-4">
          <div class="grid grid-cols-8 gap-2">
            <div class="col-span-full text-center"><h4>Basket</h4></div>
            <template v-if ="currentSale.catalogueItemSaleLines.length + currentSale.bikeSaleLines.length > 0">
              <div class="col-span-1"></div>
              <div class="col-span-4 text-center"><h5>Item</h5></div>
              <div class="col-span-1 text-center"><h5>Qty</h5></div>
              <div class="col-span-2 text-center"><h5>Price</h5></div>
            </template>
            <div v-if="currentSale.catalogueItemSaleLines.length > 0" class="col-span-full"><h5>Catalogue Items</h5></div>
            <template v-for="line in currentSale.catalogueItemSaleLines" :key="line.id">
              <div class="col-span-1"></div>
              <div class="col-span-4"><h6>{{line.catalogueItem.name}}</h6></div>
              <div class="col-span-1 text-right"><h6>{{line.quantity}}</h6></div>
              <div class="col-span-2 text-right"><h6>{{(line.salePrice / 100).toFixed(2)}}</h6></div>
            </template>
            <div v-if="currentSale.bikeSaleLines.length > 0" class="col-span-full"><h5>Bikes</h5></div>
            <template v-for="line in currentSale.bikeSaleLines" :key="line.id">
              <div class="col-span-1"></div>
              <div class="col-span-4"><h6>{{line.bike.make}} {{line.bike.model}}</h6></div>
              <div class="col-span-1"><h6>1</h6></div>
              <div class="col-span-2"><h6>{{(line.salePrice / 100).toFixed(2)}}</h6></div>
            </template>
            <div class="col-span-full h-10"></div>
            <div class="col-span-6 text-center"><h5>Total</h5></div>
            <div class="col-span-2 text-right"><h5>{{ (totalSalePrice / 100).toFixed(2) }}</h5></div>
          </div>
        </div>
      </div>
    </div>
  </Card>

  <Modal v-if="selectedItem" :active-modal="showQuantityModal" @close="closeQuantityModal" title="Quantity">
    <div class="grid grid-cols-2 gap-5">
      <div class="col-span-1">
        <CatalogueItemCard :item-details="selectedItem"/>
      </div>
      <div class="col-span-1">
        <div class="grid grid-cols-3 gap-2">
          <div class="col-span-3">
            <TextInput
              type="number"
              label="Enter Quantity"
              v-model="quantity"
            ></TextInput>
          </div>

          <div class="col-span-1">
            <Button text="Clear" @click="() => quantity = 0" class="w-full"/>
          </div>
          <div class="col-span-1">
            <Button text="-" @click="() => quantity > 0 ? quantity-- : 0" class="w-full"/>
          </div>
          <div class="col-span-1">
            <Button text="+" @click="() => quantity++" class="w-full"/>
          </div>
          <div class="col-span-1" v-for="qty in [1, 2, 3, 4, 5, 6, 7, 8, 9]" :key="qty">
            <Button :text="qty.toString()" @click="() => quantity = qty" class="w-full"/>
          </div>
        </div>
      </div>
      <div class="col-span-2">
        <Button text="Add" @click="addItemToSale" class="w-full"/>

      </div>
    </div>
  </Modal>

</template>

<style scoped lang="scss">

</style>
