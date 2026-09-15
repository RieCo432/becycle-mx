<script setup>
import {ref} from 'vue';
import requests from '@/requests';
import FormStepNavigation from '@/components/Forms/FormStepNavigation.vue';
import {useToast} from 'vue-toastification';
import DashButton from '@/components/Button/index.vue';
import PointOfSale from '@/views/sales/PointOfSale.vue';
import SaleSummaryCard from '@/components/Card/SaleSummaryCard.vue';
import {VueSpinner} from 'vue3-spinners';

const toast = useToast();


const emit = defineEmits(['goBack', 'update:draft', 'noSaleRequired']);
const props = defineProps({
  contract: {
    type: Object,
    required: true,
  },
});

function goBack() {
  if (checkCurrentlyProcessing()) return;
  emit('goBack');
}

const processingSubmit = ref(false);
function checkCurrentlyProcessing() {
  if (processingSubmit.value) {
    toast.warning('Please wait for the previous action to complete');
    return true;
  }
  return false;
}

function startSale() {
  if (checkCurrentlyProcessing()) {
    return;
  }
  processingSubmit.value = true;
  requests.postNewSale()
    .then((response) => {
      toast.success('Sale Created', {timeout: 2000});
      requests.putDraftContractSaleHeader(props.contract.id, response.data.id)
        .then((response) => {
          toast.success('Sale attached to contract.', {timeout: 2000});
          processingSubmit.value = false;
          emit('update:draft', response.data);
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          processingSubmit.value = false;
        });
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
      processingSubmit.value = false;
    });
}

function submit() {
  if (checkCurrentlyProcessing()) {
    return;
  }
  processingSubmit.value = true;
  requests.getDraftContract(props.contract.id)
    .then((response) => {
      if (!response.data.saleHeaderId || !response.data.saleHeader.transactionHeaderId) {
        toast.error('Cannot continue while sale is not completed.', {timeout: 5000});
        return;
      }
      emit('update:draft', response.data);
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
    })
    .finally(() => {
      processingSubmit.value = false;
    });
}

function cancelSale() {
  if (checkCurrentlyProcessing()) {
    return;
  }
  processingSubmit.value = true;
  if (confirm('Are you sure you want to cancel this sale?')) {
    requests.deleteDraftContractSale(props.contract.id)
      .then((response) => {
        emit('update:draft', response.data);
      })
      .catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      })
      .finally(() => {
        processingSubmit.value = false;
      });
  }
}

</script>

<template>
  <div
    class="grid lg:grid-cols-2 md:grid-cols-2 grid-cols-1 gap-5">
    <template v-if="!contract.saleHeaderId">
      <div class="lg:col-span-2 md:col-span-2 col-span-1">
        <h4 class="text-base text-slate-800 dark:text-slate-300 mb-6">
          Were any parts sold?
        </h4>
      </div>

      <div class="col-span-1">
        <DashButton
          class="w-full"
          :is-disabled="processingSubmit"
          @click="emit('noSaleRequired')">
          <template v-if="!processingSubmit">
            No
          </template>
          <template v-else>
            <VueSpinner size="20px" class="text-white"/>
          </template>
        </DashButton>
      </div>
      <div class="col-span-1">
        <DashButton
          class="w-full"
          @click="startSale"
          :is-disabled="processingSubmit">
          <template v-if="!processingSubmit">
            Yes
          </template>
          <template v-else>
            <VueSpinner size="20px" class="text-white"/>
          </template>
        </DashButton>
      </div>
    </template>
    <template v-else-if="contract.saleHeaderId && !contract.saleHeader.transactionHeaderId">
      <div class="col-span-full">
        <PointOfSale
          noAllowNew
          noAllowBikes
          :continue-sale-header-id="contract.saleHeaderId"
          @saleCompleted="submit"
          checkoutWarning="If paying cash, make sure the client still has enough money to pay for the deposit."
        />
      </div>
      <div class="col-span-full">
        <DashButton
          class="w-full"
          @click="cancelSale"
          :is-disabled="processingSubmit">
          <template v-if="!processingSubmit">
            Cancel Sale
          </template>
          <template v-else>
            <VueSpinner size="20px" class="text-white"/>
          </template>
        </DashButton>
      </div>
    </template>
    <template v-else>
      <div class="col-span-full">
        <SaleSummaryCard :sale-header="contract.saleHeader"/>
      </div>
    </template>
    <div class="col-span-full">
      <FormStepNavigation
        :processing-submit="processingSubmit"
        :submit="submit"
        :goBack="goBack"/>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
