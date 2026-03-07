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
import BikeOverviewCard from '@/components/Card/BikeOverviewCard.vue';
import {ref, watch} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';

const toast = useToast();
export default {
  name: 'PointOfSale',
  components: {
    ComboboxTextInput,
    BikeOverviewCard, BikeCatalogue, Icon, Modal, TextInput, CatalogueItemCard, Card, Button,
  },
  setup(props, context) {
    const revenueAccounts = ref([]);
    const assetAccounts = ref([]);
    const currentSale = ref(null);
    const openSales = ref([]);

    const saleCheckoutSchema = yup.object().shape({
      hasCatalogueItemSaleLines: yup.boolean(),
      catalogueItemRevenueAccount: yup.object().when('hasCatalogueItemSaleLines', {
        is: true,
        then: () => yup.object().shape({
          id: yup.string().uuid().required(' The revenue account id is required '),
          name: yup.string().required(' The revenue account name is required '),
        })
          .required('This is required for selling catalogue items.'),
        otherwise: () => yup.object().nullable(),
      }),
      hasBikeSaleLines: yup.boolean(),
      bikeRevenueAccount: yup.object().when('hasBikeSaleLines', {
        is: true,
        then: () => yup.object().shape({
          id: yup.string().uuid().required(' The revenue account id is required '),
          name: yup.string().required(' The revenue account name is required '),
        })
          .required('This is required for selling bikes.'),
        otherwise: () => yup.object().nullable(),
      }),
      paymentAssetAccount: yup.object().shape({
        id: yup.string().uuid().required(' The asset account id is required '),
        name: yup.string().required(' The asset account name is required '),
      })
        .required('Select the payment asset account.'),
      username: yup.string().required(' The username is required '),
      passwordOrPin: yup.string().required(' The password or pin is required '),
    });

    const {handleSubmit, handleReset: resetCheckoutForm} = useForm({
      validationSchema: saleCheckoutSchema,
      keepValuesOnUnmount: true,
    });

    const {
      value: hasCatalogueItemSaleLines,
      errorMessage: hasCatalogueItemSaleLinesError,
    } = useField('hasCatalogueItemSaleLines');
    const {
      value: catalogueItemRevenueAccount,
      errorMessage: catalogueItemRevenueAccountError,
    } = useField('catalogueItemRevenueAccount');
    const {value: hasBikeSaleLines, errorMessage: hasBikeSaleLinesError} = useField('hasBikeSaleLines');
    const {value: bikeRevenueAccount, errorMessage: bikeRevenueAccountError} = useField('bikeRevenueAccount');
    const {value: paymentAssetAccount, errorMessage: paymentAssetAccountError} = useField('paymentAssetAccount');
    const {value: username, errorMessage: usernameError} = useField('username');
    const {value: passwordOrPin, errorMessage: passwordOrPinError} = useField('passwordOrPin');

    function getSales() {
      requests.getSales(true, false).then((response) => {
        openSales.value = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    }

    watch(
      () => currentSale.value,
      (newValue) => {
        if (newValue) {
          hasCatalogueItemSaleLines.value = newValue.catalogueItemSaleLines.length > 0;
          hasBikeSaleLines.value = newValue.bikeSaleLines.length > 0;
        }
      },
      {deep: true},
    );

    const submitSaleCheckout = handleSubmit(() => {
      const catalogueItemTotalSalePrice = currentSale.value
        .catalogueItemSaleLines
        .reduce((total, line) => total + line.salePrice, 0);
      const bikeTotalSalePrice = currentSale.value
        .bikeSaleLines
        .reduce((total, line) => total + line.salePrice, 0);
      const totalSalePrice = catalogueItemTotalSalePrice + bikeTotalSalePrice;

      if (totalSalePrice <= 0) {
        toast.error('Sale price must be above 0!', {timeout: 2000});
        return;
      }

      const saleTransactionsHeaderDraft = {
        transactionHeader: {
          event: 'sale',
        },
        transactionLines: [
          {amount: totalSalePrice, accountId: paymentAssetAccount.value.id},
          ...(hasCatalogueItemSaleLines.value ?
            [{
              amount: -catalogueItemTotalSalePrice,
              accountId: catalogueItemRevenueAccount.value.id,
            }] :
            []),
          ...(hasBikeSaleLines.value ?
            [{
              amount: -bikeTotalSalePrice,
              accountId: bikeRevenueAccount.value.id,
            }] :
            []),
        ],
        attemptAutoPost: false,
      };

      requests.createTransaction(saleTransactionsHeaderDraft).then((response) => {
        toast.success('Transaction created', {timeout: 2000});

        requests.patchSalePayment(
          currentSale.value.id,
          response.data.id,
          username.value,
          passwordOrPin.value).then((response) => {
          toast.success('Sale completed!', {timeout: 2000});
          currentSale.value = null;
        });
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      revenueAccounts,
      assetAccounts,
      currentSale,
      catalogueItemRevenueAccount,
      catalogueItemRevenueAccountError,
      bikeRevenueAccount,
      bikeRevenueAccountError,
      paymentAssetAccount,
      paymentAssetAccountError,
      hasCatalogueItemSaleLines,
      hasCatalogueItemSaleLinesError,
      hasBikeSaleLines,
      hasBikeSaleLinesError,
      username,
      usernameError,
      passwordOrPin,
      passwordOrPinError,
      submitSaleCheckout,
      resetCheckoutForm,
      getSales,
      openSales,
    };
  },
  data() {
    return {
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
      selectedBike: null,
      showNewBikeSalePriceModal: false,
      isCheckout: false,
      activeUsers: [],
      userSelectionOptionsStatic: false,
      browseSales: false,
    };
  },
  created() {
    this.getSales();
    requests.getItemCatalogue(false).then((response) => {
      this.catalogueItems = response.data;
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });
    requests.getAccounts([
      {name: 'type', value: 'revenue'},
      {name: 'type', value: 'asset'},
      {name: 'ui_filters', value: 'sale'},
    ]).then((response) => {
      this.revenueAccounts = response.data.filter((account) => account.type === 'revenue');
      this.assetAccounts = response.data.filter((account) => account.type === 'asset');
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    });

    requests.getActiveUsers().then((response) => {
      this.activeUsers = response.data.map((user) => user.username);
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
      this.browseSales = false;
      this.currentSale = this.openSales.find((sale) => sale.id === saleId);
      toast.success('Sale Continued!', {timeout: 2000});
    },
    addItemToSale() {
      const sameItemInSale = this.currentSale.catalogueItemSaleLines
        .find((line) => line.catalogueItemId === this.selectedItem.id);
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
      if (this.quantity > 0) {
        this.showQuantityModal = false;
        this.selectedItem = null;
      }
      this.quantity = 0;
    },
    closeEditQuantityModal() {
      this.showEditQuantityModal = false;
      this.selectedItem = null;
      this.quantity = 0;
    },
    removeCatalogueItemSaleLine(catalogueItemSaleLineId) {
      requests.deleteCatalogueItemSaleLine(catalogueItemSaleLineId).then(() => {
        this.currentSale.catalogueItemSaleLines = this.currentSale.catalogueItemSaleLines
          .filter((line) => line.id !== catalogueItemSaleLineId);
        toast.success('Item removed from sale!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    updateItemQuantity() {
      const catalogueItemSaleLine = this.currentSale.catalogueItemSaleLines
        .find((line) => line.catalogueItemId === this.selectedItem.id);
      requests.putUpdateCatalogueItemSaleLine(catalogueItemSaleLine.id, {
        quantity: this.quantity,
        salePrice: this.selectedItem.recommendedRetailPrice * this.quantity,
      }).then((result) => {
        const indexInArr = this.currentSale.catalogueItemSaleLines
          .findIndex((line) => line.id === catalogueItemSaleLine.id);
        this.currentSale.catalogueItemSaleLines.splice(indexInArr, 1, result.data);
        toast.success('Item quantity updated!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
      this.closeEditQuantityModal();
    },
    openEditQuantityModal(lineId) {
      this.selectedItem = this.currentSale.catalogueItemSaleLines
        .find((line) => line.id === lineId)
        .catalogueItem;
      this.quantity = this.currentSale.catalogueItemSaleLines.find((line) => line.id === lineId).quantity;
      this.showEditQuantityModal = true;
    },
    editItemSalePrice(lineId) {
      const line = this.currentSale.catalogueItemSaleLines.find((line) => line.id === lineId);
      this.selectedItem = line.catalogueItem;
      this.newSalePrice = line.salePrice / 100;
      this.editSalePriceActive = true;
    },
    setNewItemSalePrice() {
      const line = this.currentSale.catalogueItemSaleLines
        .find((line) => line.catalogueItem.id === this.selectedItem.id);

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
      const sameBikeInSale = this.currentSale.bikeSaleLines.find((line) => line.bike.id === bike.id);
      if (!sameBikeInSale) {
        const bikeSaleLine = {
          saleHeaderId: this.currentSale.id,
          bikeId: bike.id,
          salePrice: bike.roughValue ? bike.roughValue : 0,
        };
        requests.postBikeSaleLine(bikeSaleLine).then((response) => {
          this.currentSale.bikeSaleLines.push(response.data);
          toast.success('Bike added to sale!', {timeout: 2000});
          if (!bike.roughValue) {
            toast.warning('Bike rough value not set, please set it!', {timeout: 2000});
            this.selectedBike = response.data.bike;
            this.newSalePrice = 0;
            this.showNewBikeSalePriceModal = true;
          }
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
      } else {
        toast.error('Bike already in sale!', {timeout: 2000});
      }
      ;
    },
    removeBikeSaleLine(bikeSaleLineId) {
      requests.deleteBikeSaleLine(bikeSaleLineId).then(() => {
        this.currentSale.bikeSaleLines = this.currentSale.bikeSaleLines.filter((line) => line.id !== bikeSaleLineId);
        toast.success('Bike removed from sale!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    editBikeSalePrice(bikeSaleLineId) {
      const bikeSaleLine = this.currentSale.bikeSaleLines.find((line) => line.id === bikeSaleLineId);
      this.selectedBike = bikeSaleLine.bike;
      this.newSalePrice = bikeSaleLine.salePrice / 100;
      this.editSalePriceActive = true;
    },
    setNewBikeSalePrice() {
      const bikeSaleLine = this.currentSale.bikeSaleLines.find((line) => line.bike.id === this.selectedBike.id);
      requests.putUpdateBikeSaleLine(bikeSaleLine.id, {
        salePrice: this.newSalePrice * 100,
      }).then((response) => {
        const indexInArr = this.currentSale.bikeSaleLines.findIndex((line) => line.id === response.data.id);
        this.currentSale.bikeSaleLines.splice(indexInArr, 1, response.data);
        toast.success('Sale price updated!', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
      this.editSalePriceActive = false;
      this.closeNewBikeSalePriceModal();
    },
    closeNewBikeSalePriceModal() {
      if (this.newSalePrice > 0) {
        this.showNewBikeSalePriceModal = false;
        this.selectedBike = null;
      }
    },
    checkoutSale() {
      if (this.currentSale.bikeSaleLines.length + this.currentSale.catalogueItemSaleLines.length === 0) {
        toast.error('Nothing in sale!', {timeout: 2000});
        return;
      }
      this.catalogueItemRevenueAccount = {
        id: '',
        name: '',
      };
      this.bikeRevenueAccount = {
        id: '',
        name: '',
      };
      this.paymentAssetAccount = {
        id: '',
        name: '',
      };
      this.username = '';
      this.isCheckout = true;
    },
    cancelCheckout() {
      this.isCheckout = false;
      this.showItems = null;
      this.showBikes = null;
      toast.warning('Checkout cancelled!', {timeout: 2000});
    },
    selectUser(event, i) {
      if (i !== -1) {
        this.username = this.filtered_working_user_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    makeAccountLegible(account) {
      return `${account.name}`;
    },
    selectCatalogueItemRevenueAccount(event, i) {
      if (i !== -1) {
        this.catalogueItemRevenueAccount = this.filtered_catalogue_item_revenue_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectBikeRevenueAccount(event, i) {
      if (i !== -1) {
        this.bikeRevenueAccount = this.filtered_bike_revenue_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    selectPaymentAssetAccount(event, i) {
      if (i !== -1) {
        this.paymentAssetAccount = this.filtered_payment_asset_account_suggestions[i];
        this.userSelectionOptionsStatic = false;
      }
    },
    closeSale() {
      this.isCheckout = false;
      this.browseSales = false;
      this.currentSale = null;
      this.showItems = null;
      this.showBikes = null;
      this.showEditQuantityModal = false;
      this.showNewBikeSalePriceModal = false;
      this.editSalePriceActive = false;
      this.selectedItem = null;
      this.selectedBike = null;
      this.newSalePrice = 0;
    },
  },
  computed: {
    totalSalePrice() {
      return this.currentSale.catalogueItemSaleLines.reduce((total, line) => total + line.salePrice, 0) +
        this.currentSale.bikeSaleLines.reduce((total, line) => total + line.salePrice, 0);
    },
    filtered_working_user_suggestions() {
      return this.username ? this.activeUsers
        .filter((suggestion) =>
          suggestion
            .toLowerCase()
            .startsWith(this.username.toLowerCase()))
        .sort(this.userSortingFunction)
        .slice(0, 10) : this.activeUsers;
    },
    filtered_catalogue_item_revenue_account_suggestions() {
      return this.revenueAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.catalogueItemRevenueAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_bike_revenue_account_suggestions() {
      return this.revenueAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.bikeRevenueAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_payment_asset_account_suggestions() {
      return this.assetAccounts
        .filter((suggestion) => suggestion.name
          .toLowerCase()
          .startsWith((this.paymentAssetAccount.name ?? '').toLowerCase()))
        // .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    revenueAccountsColSpan() {
      return 3 - (this.hasCatalogueItemSaleLines ? 1 : 0) - (this.hasBikeSaleLines ? 1 : 0);
    },
  },
  watch: {
    hasBikeSaleLines(newValue) {
      if (!(newValue || this.hasCatalogueItemSaleLines) && this.isCheckout) {
        this.cancelCheckout();
      }
    },
    hasCatalogueItemSaleLines(newValue) {
      if (!(newValue || this.hasBikeSaleLines) && this.isCheckout) {
        this.cancelCheckout();
      }
    },
  },
};
</script>

<template>
  <div class="fill-page">
    <!-- TODO: I think this needs to not be a card in order to work correctly and fill the whole screen. Too much baggage in the card component-->
    <Card title="Point of Sale">
      <template v-if="currentSale === null">
        <template v-if="!browseSales">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 h-full">
            <div class="col-span-1 h-full">
              <Button class="w-full h-full dark:bg-slate-900 bg-slate-400 text-6xl" text="New Sale" @click="startNewSale"/>
            </div>
            <div class="col-span-1 h-full">
              <Button class="w-full h-full dark:bg-slate-900 bg-slate-400 text-6xl" text="Browse Sales" @click="browseSales = true"/>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="grid grid-cols-12 gap-5">
            <div class="col-span-full">
              <Button class="w-full dark:bg-slate-900 bg-slate-400" text="Back" @click="() => {browseSales = false; currentSale = null}"/>
            </div>
            <div class="col-span-4" v-for="sale in openSales" :key="sale.id">
              {{ sale }}
              <Button text="Continue Sale" @click="continueSale(sale.id)"></Button>
            </div>
          </div>
        </template>
      </template>
      <template v-else>
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-12">
            <Button class="w-full dark:bg-slate-900 bg-slate-400" text="Close Sale" @click="closeSale"/>
          </div>
          <div class="col-span-12">
            <span class="text-2xl lg:text-4xl text-slate-800 dark:text-slate-300">Sale created by {{currentSale.createdByUser.username}} on {{ new Date(Date.parse(currentSale.createdOn))
              .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'}) }} </span>
          </div>
          <div class="col-span-full 2xl:col-span-8">
            <template v-if="!isCheckout">
              <template v-if="showItems">
                <div v-if="showUsed === null" class="grid grid-cols-2 gap-5 h-full">
                  <div class="col-span-full">
                    <Button text="Back" @click="() => {showBikes = null; showItems = null}" class="w-full dark:bg-slate-900 bg-slate-400"/>
                  </div>
                  <div class="col-span-1 row-span-4">
                    <Button text="New" @click="showUsed = false" class="w-full h-full text-6xl dark:bg-slate-900 bg-slate-400 aspect-square"/>
                  </div>
                  <div class="col-span-1 row-span-4">
                    <Button text="Used" @click="showUsed = true" class="w-full h-full text-6xl dark:bg-slate-900 bg-slate-400 aspect-square"/>
                  </div>
                </div>
                <div v-else class="grid grid-cols-5 gap-5">
                  <div class="col-span-5">
                    <Button text="Back" @click="showUsed = null" class="w-full dark:bg-slate-900 bg-slate-400"/>
                  </div>
                  <div
                    v-for="item in catalogueItems.filter((item) => item.isSecondHand === showUsed)"
                    :key="item.id"
                    class="col-span-1"
                    @click="() => selectItem(item)">
                    <CatalogueItemCard :item-details="item"/>
                  </div>
                </div>
              </template>

              <template v-else-if="showBikes">
                <Button text="Back" @click="() => {showBikes = null; showItems = null}" class="w-full dark:bg-slate-900 bg-slate-400"/>
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
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 h-full">
                  <div class="col-span-1 row-span-5">
                    <Button
                      class="w-full h-full text-2xl lg:text-6xl aspect-[1.5] 2xl:aspect-square dark:bg-slate-900 bg-slate-400 text-wrap"
                      text="Add Catalogue Item"
                      @click="() => showItems = true"/>
                  </div>
                  <div class="col-span-1 row-span-5">
                    <Button
                      class="w-full h-full text-2xl lg:text-6xl aspect-[1.5] 2xl:aspect-square dark:bg-slate-900 bg-slate-400 text-wrap"
                      text="Add Bike"
                      @click="() => showBikes = true"/>
                  </div>
                </div>
              </template>
            </template>
            <template v-else>
              <form @submit.prevent="submitSaleCheckout">
                <div class="grid grid-cols-2 gap-4">
                  <div
                    v-if="hasCatalogueItemSaleLines"
                    :class="`col-span-${revenueAccountsColSpan}`">
                    <ComboboxTextInput
                      :field-model-value="catalogueItemRevenueAccount.name"
                      :suggestions="filtered_catalogue_item_revenue_account_suggestions.map(makeAccountLegible)"
                      :selected-callback="selectCatalogueItemRevenueAccount"
                      :allow-new="false"
                      :open-by-default="userSelectionOptionsStatic"
                      label="Catalogue Item Revenue Account"
                      type="text"
                      placeholder="workshop"
                      name="catalogueItemRevenueAccount"
                      v-model="catalogueItemRevenueAccount.name"
                      :error="catalogueItemRevenueAccountError"
                      @change="() => {}"
                    />
                  </div>
                  <div
                    v-if="hasBikeSaleLines"
                    :class="`col-span-${revenueAccountsColSpan}`">
                    <ComboboxTextInput
                      :field-model-value="bikeRevenueAccount.name"
                      :suggestions="filtered_bike_revenue_account_suggestions.map(makeAccountLegible)"
                      :selected-callback="selectBikeRevenueAccount"
                      :allow-new="false"
                      :open-by-default="userSelectionOptionsStatic"
                      label="Bike Sale Revenue Account"
                      type="text"
                      placeholder="workshop"
                      name="bikeRevenueAccount"
                      v-model="bikeRevenueAccount.name"
                      :error="bikeRevenueAccountError"
                      @change="() => {}"
                    />
                  </div>
                  <div class="col-span-full">
                    <ComboboxTextInput
                      :field-model-value="paymentAssetAccount.name"
                      :suggestions="filtered_payment_asset_account_suggestions.map(makeAccountLegible)"
                      :selected-callback="selectPaymentAssetAccount"
                      :allow-new="false"
                      :open-by-default="userSelectionOptionsStatic"
                      label="Payment Account"
                      type="text"
                      placeholder="workshop"
                      name="paymentAssetAccount"
                      v-model="paymentAssetAccount.name"
                      :error="paymentAssetAccountError"
                      @change="() => {}"
                    />
                  </div>
                  <div class="col-span-full">
                    <ComboboxTextInput
                      :field-model-value="username"
                      :suggestions="filtered_working_user_suggestions"
                      :selected-callback="selectUser"
                      :allow-new="false"
                      :open-by-default="userSelectionOptionsStatic"
                      label="Volunteer"
                      type="text"
                      placeholder="workshop"
                      name="username"
                      v-model="username"
                      :error="usernameError"
                      @change="() => {}"
                    />
                  </div>
                  <div class="col-span-full">
                    <TextInput
                      label="Password or Pin"
                      type="password"
                      placeholder="Password or Pin"
                      name="passwordOrPin"
                      v-model="passwordOrPin"
                      :error="passwordOrPinError"
                      hasicon/>
                  </div>
                  <div class="col-span-full">
                    <Button class="w-full" type="submit" text="Complete Sale"/>
                  </div>
                </div>
              </form>
            </template>
          </div>
          <div class="col-span-full 2xl:col-span-4 h-full relative">
            <div class="grid grid-cols-9 gap-2 divide-x divide-y dark:text-slate-300 text-slate-700 align-middle">
              <div class="col-span-full text-center"><h4>Basket</h4></div>
              <template v-if="currentSale.catalogueItemSaleLines.length + currentSale.bikeSaleLines.length > 0">
                <div class="col-span-1"></div>
                <div class="col-span-4 text-center"><h5>Item</h5></div>
                <div class="col-span-1 text-center"><h5>Qty</h5></div>
                <div class="col-span-2 text-center"><h5>Price</h5></div>
                <div class="col-span-1"></div>
              </template>
              <div v-if="currentSale.catalogueItemSaleLines.length > 0" class="col-span-full">
                <h5>Catalogue Items</h5>
              </div>
              <template v-for="line in currentSale.catalogueItemSaleLines" :key="line.id">
                <div class="col-span-1"></div>
                <div class="col-span-4"><h6>{{ line.catalogueItem.name }}</h6></div>
                <div class="col-span-1 text-right">
                  <h6 class="inline align-bottom mb-0">{{ line.quantity }}</h6>
                  <Icon
                    class="inline align-middle"
                    icon="heroicons-outline:pencil"
                    @click="openEditQuantityModal(line.id)"/>
                </div>
                <div class="col-span-2 text-right">
                  <template v-if="editSalePriceActive && selectedItem && line.catalogueItem.id === selectedItem.id">
                    <Icon
                      class="inline align-middle"
                      icon="heroicons-outline:check"
                      @click="setNewItemSalePrice"/>
                    <Icon
                      class="inline align-middle"
                      icon="heroicons-outline:x"
                      @click="() => {editSalePriceActive = false; selectedItem = null}"/>
                    <input
                      class="inline align-bottom mb-0 w-[50px] text-right input-control
                        [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none
                        [&::-webkit-inner-spin-button]:appearance-none"
                      type="number"
                      v-model="newSalePrice"
                      :placeholder="line.salePrice / 100"
                    />

                  </template>
                  <template v-else>
                    <h6 class="inline align-bottom mb-0">{{ (line.salePrice / 100).toFixed(2) }}</h6>
                    <Icon
                      class="inline align-middle"
                      icon="heroicons-outline:pencil"
                      @click="editItemSalePrice(line.id)"/>
                  </template>
                </div>
                <div class="col-span-1 justify-items-center">
                  <Icon icon="heroicons-outline:trash" @click="removeCatalogueItemSaleLine(line.id)"/>
                </div>
              </template>
              <div v-if="currentSale.bikeSaleLines.length > 0" class="col-span-full"><h5>Bikes</h5></div>
              <template v-for="line in currentSale.bikeSaleLines" :key="line.id">
                <div class="col-span-1"></div>
                <div class="col-span-4">
                  <h6>{{ line.bike.make }} {{ line.bike.model }}</h6>
                </div>
                <div class="col-span-1 text-right"><h6>-</h6></div>
                <div class="col-span-2 text-right">
                  <template v-if="editSalePriceActive && selectedBike && line.bike.id === selectedBike.id">
                    <Icon
                      class="inline align-middle"
                      icon="heroicons-outline:check"
                      @click="setNewBikeSalePrice"/>
                    <Icon
                      class="inline align-middle"
                      icon="heroicons-outline:x"
                      @click="() => {editSalePriceActive = false; selectedBike = null}"/>
                    <input
                      class="inline align-bottom mb-0 w-[50px] text-right input-control
                        [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none
                        [&::-webkit-inner-spin-button]:appearance-none"
                      type="number"
                      v-model="newSalePrice"
                      :placeholder="line.salePrice / 100"
                    />

                  </template>
                  <template v-else>
                    <h6 class="inline align-bottom mb-0">{{ (line.salePrice / 100).toFixed(2) }}</h6>
                    <Icon
                      class="inline align-middle"
                      icon="heroicons-outline:pencil"
                      @click="editBikeSalePrice(line.id)"/>
                  </template>
                </div>
                <div class="col-span-1 justify-items-center">
                  <Icon icon="heroicons-outline:trash" @click="removeBikeSaleLine(line.id)"/>
                </div>
              </template>
              <div class="col-span-full h-10"></div>
              <div class="col-span-6 text-center"><h5>Total</h5></div>
              <div class="col-span-2 text-right"><h5>{{ (totalSalePrice / 100).toFixed(2) }}</h5></div>
            </div>
            <Button v-if="!isCheckout" class="w-full absolute bottom-0" text="Checkout" @click="checkoutSale"/>
            <Button v-if="isCheckout" class="w-full absolute bottom-0" text="Cancel Checkout" @click="cancelCheckout"/>
          </div>
        </div>
      </template>
    </Card>

    <Modal
      v-if="selectedItem"
      :active-modal="showQuantityModal"
      @close="closeQuantityModal"
      title="Quantity"
    >
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

    <Modal
      v-if="selectedItem"
      :active-modal="showEditQuantityModal"
      @close="closeEditQuantityModal"
      title="Quantity">
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

    <Modal
      v-if="selectedBike"
      :active-modal="showNewBikeSalePriceModal"
      @close="closeNewBikeSalePriceModal"
      title="Price">
      <div class="grid grid-cols-2 gap-5">
        <div class="col-span-1">
          <BikeOverviewCard :bike="selectedBike"/>
        </div>
        <div class="col-span-1">
          <TextInput
            type="number"
            label="Enter Price"
            v-model="newSalePrice"
          ></TextInput>
        </div>
        <div class="col-span-2">
          <Button text="Add" @click="setNewBikeSalePrice" class="w-full"/>
        </div>
      </div>
    </Modal>
  </div>
</template>

<style scoped lang="scss">
.fill-page {
  min-height: calc(var(--vh, 1vh) * 100 - 194px);
  height: calc(var(--vh, 1vh) * 100 - 194px);
}
</style>
