<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card title="New Contract">
        <div>
          <div class="flex z-[5] items-center relative justify-center md:mx-8">
            <div
                class="relative z-[1] items-center item flex flex-start flex-1 last:flex-none group"
                v-for="(item, i) in steps"
                :key="i"
            >
              <div
                  :class="`   ${
            currentStepNumber >= i
              ? 'bg-slate-900 text-white ring-slate-900 ring-offset-2 dark:ring-offset-slate-500 ' +
                'dark:bg-slate-900 dark:ring-slate-900'
              : 'bg-white ring-slate-900 ring-opacity-70  text-slate-900 dark:text-slate-300 ' +
                'dark:bg-slate-600 dark:ring-slate-600 text-opacity-70'
          }`"
                  class="transition duration-150 icon-box md:h-12 md:w-12 h-7 w-7 rounded-full flex flex-col
                         items-center justify-center relative z-[66] ring-1 md:text-lg text-base font-medium"
              >
                <span v-if="currentStepNumber <= i"> {{ i + 1 }}</span>
                <span v-else class="text-3xl">
            <Icon icon="bx:check-double" />
          </span>
              </div>

              <div
                  class="absolute top-1/2 h-[2px] w-full"
                  :class="
            currentStepNumber >= i
              ? 'bg-slate-900 dark:bg-slate-900'
              : 'bg-[#E0EAFF] dark:bg-slate-700'
          "
              ></div>
              <div
                  class="absolute top-full text-base md:leading-6 mt-3 transition duration-150
                         md:opacity-100 opacity-0 group-hover:opacity-100"
                  :class="
            currentStepNumber >= i
              ? ' text-slate-900 dark:text-slate-300'
              : 'text-slate-500 dark:text-slate-300 dark:text-opacity-40'
          "
              >
                <span class="w-max">{{ item.title }}</span>
              </div>
            </div>
          </div>

          <div
              class="content-box mt-14 border-t border-slate-100 dark:border-slate-700 -mx-6 px-6 pt-6"
          >
            <template v-if="!promoting">
              <div v-if="currentStepNumber === 0">
                <NewContractStartForm
                  :current-contract-draft="currentContractDraft"
                  @update:currentContractDraft="updateDraft"
                />
              </div>
              <div v-if="currentStepNumber === 1">
                <NewContractClientForm
                  :contract="currentContractDraft"
                  @update:draft="updateDraft"
                  @go-back="goBack"
                />
              </div>
              <div v-if="currentStepNumber === 2">
                <NewContractBikeForm
                  :contract="currentContractDraft"
                  @update:draft="updateDraft"
                  @go-back="goBack"
                />
              </div>
              <div v-if="currentStepNumber === 3">
                <NewContractDetailsForm
                  :contract="currentContractDraft"
                  @update:draft="updateDraft"
                  @go-back="goBack"
                />
              </div>
              <div v-if="currentStepNumber === 4">
                <NewContractWorkingVolunteerForm
                  :user-sorting-function="userSortingFunction"
                  :contract="currentContractDraft"
                  @update:draft="updateDraft"
                  @go-back="goBack"
                />
              </div>
              <div v-if="currentStepNumber === 5">
                <NewContractCheckingVolunteerForm
                  :user-sorting-function="userSortingFunction"
                  :contract="currentContractDraft"
                  @update:draft="updateDraft"
                  @go-back="goBack"
                />
              </div>
              <div v-if="currentStepNumber === 6">
                <NewContractDepositForm
                  :contract="currentContractDraft"
                  @update:draft="updateDraft"
                  @go-back="goBack"
                />
              </div>
            </template>
            <div v-if="promoting" class="flex flex-col items-center text-center">
              <div>
                <h3>Finalising Contract, please wait...</h3>
              </div>
              <div>
                <VueSpinner size="100px" class="block text-sky-500" />
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>
<script setup>
import Card from '@/components/Card';
import Icon from '@/components/Icon';

import {ref} from 'vue';
import {useToast} from 'vue-toastification';

import NewContractStartForm from '@/components/Forms/NewContractStartForm.vue';
import NewContractClientForm from '@/components/Forms/NewContractClientForm.vue';
import NewContractBikeForm from '@/components/Forms/NewContractBikeForm.vue';
import NewContractDetailsForm from '@/components/Forms/NewContractDetailsForm.vue';
import NewContractWorkingVolunteerForm from '@/components/Forms/NewContractWorkingVolunteerForm.vue';
import NewContractCheckingVolunteerForm from '@/components/Forms/NewContractCheckingVolunteerForm.vue';
import NewContractDepositForm from '@/components/Forms/NewContractDepositForm.vue';
import requests from '@/requests';
import router from '@/router';
import {VueSpinner} from 'vue3-spinners';

const toast = useToast();

const steps = [
  {
    id: 1,
    title: 'Start',
  },
  {
    id: 2,
    title: 'Client Details',
  },
  {
    id: 3,
    title: 'Bike Details',
  },
  {
    id: 4,
    title: 'Contract Details',
  },
  {
    id: 5,
    title: 'Mechanic',
  },
  {
    id: 6,
    title: 'Safety Check',
  },
  {
    id: 7,
    title: 'Deposit',
  },
];

const currentStepNumber = ref(0);
const promoting = ref(false);


const currentContractDraft = defineModel();


function goBack() {
  currentStepNumber.value--;
}

function updateDraft(draft) {
  console.log('updateDraft', draft);
  currentContractDraft.value = draft;
  nextStep();
}

function nextStep() {
  if (!currentContractDraft.value.id) {
    currentStepNumber.value = 0;
    return;
  }
  if (!currentContractDraft.value.clientId) {
    currentStepNumber.value = 1;
    return;
  }
  if (!currentContractDraft.value.bikeId) {
    currentStepNumber.value = 2;
    return;
  }
  if (
    currentContractDraft.value.contractType == null ||
    currentContractDraft.value.conditionOfBike == null) {
    currentStepNumber.value = 3;
    return;
  }
  if (!currentContractDraft.value.workingUserId) {
    currentStepNumber.value = 4;
    return;
  }
  if (!currentContractDraft.value.checkingUserId) {
    currentStepNumber.value = 5;
    return;
  }
  if (!currentContractDraft.value.depositTransactionHeaders.find((th) => th.event === 'deposit_collected')) {
    currentStepNumber.value = 6;
    return;
  }
  promoteDraft();
}

function promoteDraft() {
  promoting.value = true;
  requests.patchSubmitDraftContract(currentContractDraft.value.id)
    .then((response) => {
      toast.success('Contract Recorded!', {timeout: 1000});
      router.push({path: `/contracts/${response.data.id}`, query: {showTerms: 1}});
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 5000});
      promoting.value = false;
    });
}

function userSortingFunction(user1, user2) {
  if (user1.toLowerCase() > user2.toLowerCase()) return 1;
  if (user1.toLowerCase() < user2.toLowerCase()) return -1;
  return 0;
}


</script>
<style lang="scss" scoped></style>
