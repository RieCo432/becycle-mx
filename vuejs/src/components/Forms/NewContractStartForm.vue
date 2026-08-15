<script setup>

import DashButton from '@/components/Button/index.vue';
import ContractCard from '@/components/Card/ContractDraftCard.vue';
import {defineEmits, ref, onMounted} from 'vue';
import requests from '@/requests';
import {VueSpinner} from 'vue3-spinners';
import {useToast} from 'vue-toastification';

const toast = useToast();


const props = defineProps(['currentContractDraft']);
const emit = defineEmits(['update:currentContractDraft', 'doneLoading']);

const existingContractDrafts = ref([]);
const stepLoading = ref(true);





const processingSubmit = ref(false);
function checkCurrentlyProcessing() {
  if (processingSubmit.value) {
    toast.warning('Please wait for the previous action to complete');
    return true;
  }
  return false;
}


function createNewDraft() {
  if (checkCurrentlyProcessing()) return;
  
  processingSubmit.value = true;
  requests.postNewContractDraft()
    .then((response) => {
      existingContractDrafts.value.push(response.data);
      selectDraft(response.data.id);
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 5000});
    })
    .finally(() => {
      processingSubmit.value = false;
    });
}

function selectDraft(draftId) {
  processingSubmit.value = true;
  const draft = existingContractDrafts.value.find((draft) => draft.id === draftId);
  if (draft) {
    emit('update:currentContractDraft', draft);
  }
  processingSubmit.value = false;
}

onMounted(() => {
  requests.getContracts(true)
    .then((response) => {
      existingContractDrafts.value.splice(0, existingContractDrafts.value.length, ...response.data);
      stepLoading.value = false;
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 5000});
    });
});


</script>

<template>
  <div v-if="stepLoading">
    <div class="col-span-1">
      <h4 class="text-slate-800 dark:text-slate-300 mb-6">
        <VueSpinner size="100px" class="text-sky-500"/>
      </h4>
    </div>
  </div>
  <div v-else class="grid grid-cols-1 2xl:grid-cols-2 gap-5">
    <div class="col-span-1">
      <h4 class="text-slate-800 dark:text-slate-300 mb-6">
        Create a New Contract or choose a draft to continue.
      </h4>
    </div>
    <div class="col-span-1">
      <DashButton 
        @click="createNewDraft">Create New</DashButton>
    </div>
    <template v-for="draft in existingContractDrafts" :key="draft.id">
      <div class="col-span-1">
        <ContractCard
          :contract="draft"
          :select-contract-function="selectDraft"
        />
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">

</style>
