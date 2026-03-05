<script>
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Card from '@/components/Card/index.vue';
import Button from '@/components/Button/index.vue';
import CatalogueItemCard from '@/components/Card/CatalogueItemCard.vue';
import TextInput from '@/components/TextInput/index.vue';
import Modal from '@/components/Modal/Modal.vue';
import {Icon} from '@iconify/vue';
import BikeCatalogue from '@/views/bike/BikeCatalogue.vue';

const toast = useToast();
export default {
  name: 'PointOfSale',
  components: {BikeCatalogue, Icon, Modal, TextInput, CatalogueItemCard, Card, Button},
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
      showEditQuantityModal: false,
      selectedItem: null,
      quantity: 0,
      editSalePriceActive: false,
      newSalePrice: 0,
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
      const sameItemInSale = this.currentSale.catalogueItemSaleLines.find((line) => line.catalogueItemId === this.selectedItem.id);
      if (!sameItemInSale) {
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
      } else {
        this.quantity += sameItemInSale.quantity;
        this.updateItemQuantity();
      }
      
      this.showQuantityModal = false;
    },
    selectItem(item) {
      this.selectedItem = item;
      this.quantity = 0;
      this.showQuantityModal = true;
    },
    closeQuantityModal() {
      this.showQuantityModal = false;
      this.selectedItem = null;
      this.quantity = 0;
    },
    closeEditQuantityModal() {
      this.showEditQuantityModal = false;
      this.selectedItem = null;
      this.quantity = 0;
    },
    removeCatalogueItemSaleLine(catalogueItemSaleLineId) {
      requests.deleteCatalogueItemSaleLine(catalogueItemSaleLineId).then(() => {
        this.currentSale.catalogueItemSaleLines = this.currentSale.catalogueItemSaleLines.filter(line => line.id !== catalogueItemSaleLineId);
        toast.success('Item removed from sale!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    updateItemQuantity() {
      const catalogueItemSaleLine = this.currentSale.catalogueItemSaleLines.find((line) => line.catalogueItemId === this.selectedItem.id);
      requests.putUpdateCatalogueItemSaleLine(catalogueItemSaleLine.id, {
        quantity: this.quantity,
        salePrice: this.selectedItem.recommendedRetailPrice * this.quantity,
      }).then((result) => {
        const indexInArr = this.currentSale.catalogueItemSaleLines.findIndex((line) => line.id === catalogueItemSaleLine.id);
        this.currentSale.catalogueItemSaleLines.splice(indexInArr, 1, result.data);
        toast.success('Item quantity updated!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
      this.closeEditQuantityModal();
    },
    openEditQuantityModal(lineId) {
      this.selectedItem = this.currentSale.catalogueItemSaleLines.find((line) => line.id === lineId).catalogueItem;
      this.quantity = this.currentSale.catalogueItemSaleLines.find((line) => line.id === lineId).quantity;
      this.showEditQuantityModal = true;
    },
    editSalePrice(lineId) {
      const line = this.currentSale.catalogueItemSaleLines.find((line) => line.id === lineId);
      this.selectedItem = line.catalogueItem;
      this.newSalePrice = line.salePrice / 100;
      this.editSalePriceActive = true;
    },
    setNewSalePrice() {
      const line = this.currentSale.catalogueItemSaleLines.find((line) => line.catalogueItem.id === this.selectedItem.id);

      requests.putUpdateCatalogueItemSaleLine(line.id, {
        quantity: line.quantity,
        salePrice: this.newSalePrice * 100,
      }).then((response) => {
        const indexInArr = this.currentSale.catalogueItemSaleLines.findIndex((line) => line.id === response.data.id);
        this.currentSale.catalogueItemSaleLines.splice(indexInArr, 1, response.data);
        toast.success('Sale price updated!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
      this.editSalePriceActive = false;
    },
    addBikeToSale(bike) {
      console.log(bike);
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
  <div>
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
              <div v-if="showUsed === null" class="grid grid-cols-2 gap-5 h-full">
                <div class="col-span-full">
                  <Button text="Back" @click="() => {showBikes = null; showItems = null}" class="w-full"/>
                </div>
                <div class="col-span-1 row-span-4">
                  <Button text="New" @click="showUsed = false" class="w-full h-full text-6xl"/>
                </div>
                <div class="col-span-1 row-span-4">
                  <Button text="Used" @click="showUsed = true" class="w-full h-full text-6xl"/>
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
              <BikeCatalogue
                class="mt-3"
                outer-grid-col-classes="grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3"
                inner-grid-col-span-classes="col-span-1 lg:col-span-1 2xl:col-span-2"
                inner-grid-col-classes="grid-cols-1 2xl:grid-cols-2"
                :include-rental="false"
              >
                <template v-slot:specialAction="props">
                  <Button class="col" @click="addBikeToSale(props.bike)">Add To Sale</Button>
                </template>
              </BikeCatalogue>
            </template>

            <template v-else>
              <div class="grid grid-cols-2 gap-5 h-full">
                <div class="col-span-1 row-span-5">
                  <Button class="w-full h-full text-6xl" text="Add Catalogue Item" @click="() => showItems = true"></Button>
                </div>
                <div class="col-span-1 row-span-5">
                  <Button class="w-full h-full text-6xl" text="Add Bike" @click="() => showBikes = true"></Button>
                </div>
              </div>
            </template>
          </div>
          <div class="col-span-4">
            <div class="grid grid-cols-9 gap-2 divide-x divide-y dark:text-slate-300 text-slate-700 align-middle">
              <div class="col-span-full text-center"><h4>Basket</h4></div>
              <template v-if ="currentSale.catalogueItemSaleLines.length + currentSale.bikeSaleLines.length > 0">
                <div class="col-span-1"></div>
                <div class="col-span-4 text-center"><h5>Item</h5></div>
                <div class="col-span-1 text-center"><h5>Qty</h5></div>
                <div class="col-span-2 text-center"><h5>Price</h5></div>
                <div class="col-span-1"></div>
              </template>
              <div v-if="currentSale.catalogueItemSaleLines.length > 0" class="col-span-full"><h5>Catalogue Items</h5></div>
              <template v-for="line in currentSale.catalogueItemSaleLines" :key="line.id">
                <div class="col-span-1"></div>
                <div class="col-span-4"><h6>{{line.catalogueItem.name}}</h6></div>
                <div class="col-span-1 text-right">
                  <h6 class="inline align-bottom mb-0">{{line.quantity}}</h6>
                  <Icon class="inline align-middle" icon="heroicons-outline:pencil" @click="openEditQuantityModal(line.id)"/></div>
                <div class="col-span-2 text-right">
                  <template v-if="editSalePriceActive && line.catalogueItem.id === selectedItem.id">
                    <Icon class="inline align-middle" icon="heroicons-outline:check" @click="setNewSalePrice"/>
                    <Icon class="inline align-middle" icon="heroicons-outline:x" @click="() => {editSalePriceActive = false; selectedItem = null}"/>
                    <input
                      class="inline align-bottom mb-0 w-[50px] text-right input-control [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                      type="number"
                      v-model="newSalePrice"
                      :placeholder="line.salePrice / 100"
                    />

                  </template>
                  <template v-else>
                    <h6 class="inline align-bottom mb-0">{{(line.salePrice / 100).toFixed(2)}}</h6>
                    <Icon class="inline align-middle" icon="heroicons-outline:pencil" @click="editSalePrice(line.id)"/>
                  </template>
                </div>
                <div class="col-span-1 justify-items-center"><Icon icon="heroicons-outline:trash" @click="removeCatalogueItemSaleLine(line.id)"/></div>
              </template>
              <div v-if="currentSale.bikeSaleLines.length > 0" class="col-span-full"><h5>Bikes</h5></div>
              <template v-for="line in currentSale.bikeSaleLines" :key="line.id">
                <div class="col-span-1"></div>
                <div class="col-span-4"><h6>{{line.bike.make}} {{line.bike.model}}</h6></div>
                <div class="col-span-1"><h6>1</h6></div>
                <div class="col-span-2"><h6>{{(line.salePrice / 100).toFixed(2)}}</h6></div>
                <div class="col-span-1"><Icon icon="heroicons-outline:trash"/></div>
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

    <Modal v-if="selectedItem" :active-modal="showEditQuantityModal" @close="closeEditQuantityModal" title="Quantity">
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
          <Button text="Add" @click="updateItemQuantity" class="w-full"/>

        </div>
      </div>
    </Modal>
  </div>
</template>

<style scoped lang="scss">

</style>
