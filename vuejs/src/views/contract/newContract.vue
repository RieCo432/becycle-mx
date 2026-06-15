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
            <div v-if="currentStepNumber === 0">
              <NewContractStartForm
                :current-contract-draft="currentContractDraft"
                @update:currentContractDraft="updateDraft"
              />
            </div>
            <div v-if="currentStepNumber === 1">
              <NewContractClientForm
                :draft="currentContractDraft"
                @update:draft="updateDraft"
                @go-back="goBack"
              />
            </div>
<!--            <form @submit.prevent="submit" @keydown.enter="() => {}">-->
<!--              -->

<!--              <div v-if="stepNumber === 2">-->
<!--                <NewContractBikeForm />-->
<!--              </div>-->
<!--              <div v-if="stepNumber === 3">-->
<!--                <NewContractDetailsForm />-->
<!--              </div>-->
<!--              <div v-if="stepNumber === 4">-->
<!--                <NewContractWorkingVolunteerForm />-->
<!--              </div>-->
<!--              <div v-if="stepNumber === 5">-->
<!--                <NewContractCheckingVolunteerForm />-->
<!--              </div>-->
<!--              <div v-if="stepNumber === 6">-->
<!--                <NewContractDepositForm />-->
<!--              </div>-->
<!--              -->

<!--              <div-->
<!--                  class="mt-10"-->
<!--                  :class="stepNumber > 0 ? 'flex justify-between' : ' text-right'"-->
<!--              >-->
<!--                <Button-->
<!--                    @click.prevent="prev()"-->
<!--                    text="prev"-->
<!--                    btnClass="btn-dark"-->
<!--                    v-if="this.stepNumber !== 0"-->
<!--                />-->
<!--                <Button-->
<!--                    v-if="stepNumber !== 0"-->
<!--                    btnClass="btn-dark"-->
<!--                    :disabled="stepIsLoading">-->
<!--                  <span v-if="!stepIsLoading">{{stepNumber !== this.steps.length - 1 ? 'next' : 'submit'}}</span>-->
<!--                  <VueSpinner v-if="stepIsLoading" size="20px" class="text-sky-500"/>-->
<!--                </Button>-->
<!--              </div>-->
<!--            </form>-->
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>
<script setup>
import Card from '@/components/Card';
import Button from '@/components/Button';
import Icon from '@/components/Icon';

import {ref} from 'vue';
import {useToast} from 'vue-toastification';

import {VueSpinner} from 'vue3-spinners';

import NewContractStartForm from '@/components/Forms/NewContractStartForm.vue';
import NewContractClientForm from '@/components/Forms/NewContractClientForm.vue';
// import NewContractBikeForm from '@/components/Forms/NewContractBikeForm.vue';
// import NewContractDetailsForm from '@/components/Forms/NewContractDetailsForm.vue';
// import NewContractWorkingVolunteerForm from '@/components/Forms/NewContractWorkingVolunteerForm.vue';
// import NewContractCheckingVolunteerForm from '@/components/Forms/NewContractCheckingVolunteerForm.vue';
// import NewContractDepositForm from '@/components/Forms/NewContractDepositForm.vue';

const toast = useToast();
const OFFICIAL_NAME = import.meta.env.VITE_OFFICIAL_NAME;


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
    title: 'Deposit',
  },
  {
    id: 6,
    title: 'Mechanic',
  },
  {
    id: 7,
    title: 'Safety Check',
  },
];

const currentStepNumber = ref(0);



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
  if (currentContractDraft.value.id) currentStepNumber.value = 1;
  if (currentContractDraft.value.clientId) currentStepNumber.value = 2;
}


</script>
<style lang="scss" scoped></style>
