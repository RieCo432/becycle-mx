<script setup>
import requests from '@/requests';
import {computed, ref} from 'vue';
import Card from '@/components/Card/index.vue';
import {useToast} from 'vue-toastification';
import ContractsToForfeitTable from '@/components/Tables/ContractsToForfeitTable.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import Alert from '@/components/Alert/index.vue';
import moneyUtils from '@/util/moneyUtils';
import Button from '@/components/Button';
import {Icon} from '@iconify/vue';
import Tooltip from '@/components/Tooltip/index.vue';
import {throttle} from 'lodash-es';
import {useRouter} from 'vue-router';

const router = useRouter();
const toast = useToast();
const forfeitableContracts = ref([]);
const loadingContracts = ref(true);
const revenueAccounts = ref([]);
const liabilityAccounts = ref([]);
const processing = ref(false);


const columns = [
  {
    label: 'Client',
    field: 'client',
  },
  {
    label: 'Bike',
    field: 'bike',
  },
  {
    label: 'Start Date',
    field: 'startDate',
  },
  {
    label: 'End Date',
    field: 'endDate'},
  {
    label: 'Dormant Date',
    field: 'dormantDate',
  },
  {
    label: 'Liability',
    field: 'liability',
  },
  {
    label: 'Action',
    field: 'action',
  },
];


requests.getForfeitableContracts()
  .then((response) => {
    forfeitableContracts.value = response.data
      .map((contract) => {
        const lastLiabilityDormantTransactionHeader = contract.depositTransactionHeaders
          .filter((th) => th.event === 'liability_dormant')
          .sort((thA, thB) => new Date(thB.postedOn) - new Date(thA.postedOn))[0];

        if (!lastLiabilityDormantTransactionHeader) {
          console.log('No liability dormant transaction header found for contract', contract);
          return undefined;
        }

        const liability = lastLiabilityDormantTransactionHeader.transactionLines
          .filter((tl) => tl.account.name.includes('dormant'))[0]?.amount;
        if (!liability) {
          console.log('No liability amount found for contract', contract);
          return undefined;
        }

        return {
          id: contract.id,
          client: contract.client,
          bike: contract.bike,
          startDate: contract.startDate,
          endDate: contract.endDate,
          dormantDate: lastLiabilityDormantTransactionHeader.postedOn,
          liability: liability,
        };
      })
      .filter((contract) => contract !== undefined)
      .sort((contractA, contractB) => new Date(contractB.dormantDate) - new Date(contractA.dormantDate))
      .reverse();

    loadingContracts.value = false;
  })
  .catch((error) => {
    toast.error(error.response.data.detail.description, {time: 5000});
  });


requests.getAccounts([
  {name: 'types', value: 'revenue'},
  {name: 'for_user', value: true},
  {name: 'ui_filters', value: 'transfer'},
]).then((response) => {
  revenueAccounts.value = response.data;
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 2000});
});


requests.getAccounts([
  {name: 'types', value: 'liability'},
  {name: 'for_user', value: true},
  {name: 'ui_filters', value: 'transfer'},
]).then((response) => {
  liabilityAccounts.value = response.data;
}).catch((error) => {
  toast.error(error.response.data.detail.description, {timeout: 2000});
});


const liabilityAccount = ref({name: null, id: null, balance: null});
const liabilityAccountError = ref(null);

const revenueAccount = ref({name: null, id: null, balance: null});
const revenueAccountError = ref(null);

const filteredRevenueAccountSuggestions = computed({
  get: () => {
    return revenueAccounts.value
      .filter((suggestion) => suggestion.name
        .toLowerCase()
        .startsWith((revenueAccount.value.name ?? '').toLowerCase()))
    // .sort(this.userSortingFunction)
      .slice(0, 10);
  },
});

const filteredLiabilityAccountSuggestions = computed({
  get: () => {
    return liabilityAccounts.value
      .filter((suggestion) => suggestion.name
        .toLowerCase()
        .startsWith((liabilityAccount.value.name ?? '').toLowerCase()))
      .slice(0, 10);
  },
});

function selectRevenueAccount(event, i) {
  if (i !== -1) {
    const account = filteredRevenueAccountSuggestions.value[i];

    revenueAccount.value = {
      id: account.id,
      name: account.name,
      balance: account.balance,
    };
    revenueAccountError.value = null;
  }
}

function selectLiabilityAccount(event, i) {
  if (i !== -1) {
    const account = filteredLiabilityAccountSuggestions.value[i];
    liabilityAccount.value = {
      id: account.id,
      name: account.name,
      balance: account.balance,
    };
    liabilityAccountError.value = null;
  }
}

function makeAccountLegible(account) {
  return `${account.name}`;
}

function refreshAccountBalances() {
  if (revenueAccount.value.id) {
    requests.getAccount(revenueAccount.value.id)
      .then((response) => {
        revenueAccount.value.balance = response.data.balance;
      });
  }
  if (liabilityAccount.value.id) {
    requests.getAccount(liabilityAccount.value.id)
      .then((response) => {
        liabilityAccount.value.balance = response.data.balance;
      });
  }
}

const refreshAccountBalancesThrottled = throttle(refreshAccountBalances, 5000);

function forfeitContract(contractId) {
  if (processing.value) {
    toast.error('Operation currently in progress', {timeout: 1000});
    return;
  }

  if (!revenueAccount.value.name || !revenueAccount.value.id) {
    revenueAccountError.value = 'Please select a revenue account';
  }
  if (!liabilityAccount.value.name || !liabilityAccount.value.id) {
    liabilityAccountError.value = 'Please select a liability account';
  }
  if (revenueAccountError.value || liabilityAccountError.value) {
    return;
  }

  const indexInArray = forfeitableContracts.value.findIndex((contract) => contract.id === contractId);
  if (indexInArray === -1) {
    toast.error('Contract not found', {timeout: 1000});
    return;
  }

  const liabilityAmount = forfeitableContracts.value[indexInArray].liability;

  processing.value = true;

  requests.patchContractForfeit(contractId, revenueAccount.value.id)
    .then((response) => {
      if (response.data.id !== contractId) {
        toast.error('A different contract was forfeited', {timeout: 1000});
        console.error('A different contract was forfeited');
        return;
      }

      revenueAccount.value.balance += liabilityAmount;
      liabilityAccount.value.balance -= liabilityAmount;
      refreshAccountBalancesThrottled();

      forfeitableContracts.value.splice(indexInArray, 1);

      toast.success('Contract forfeited', {timeout: 1000});
    })
    .catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 1000});
    })
    .finally(() => {
      processing.value = false;
    });
}

function viewContract(contractId) {
  const routeData = router.resolve({path: `/contracts/${contractId}`});
  window.open(routeData.href, '_blank');
}

function ignoreContract(contractId) {
  const indexInArray = forfeitableContracts.value.findIndex((contract) => contract.id === contractId);
  forfeitableContracts.value.splice(indexInArray, 1);
  toast.success('Ignored for now', {timeout: 1000});
}

</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-2">
      <Card title="Controls">

          <div class="grid grid-cols-1 gap-5">
            <div class="col-span-1">
              <ComboboxTextInput
                :field-model-value="revenueAccount.name"
                :suggestions="filteredRevenueAccountSuggestions.map(makeAccountLegible)"
                :selected-callback="selectRevenueAccount"
                :allow-new="false"
                :open-by-default="false"
                label="Revenue Account"
                type="text"
                placeholder="Forfeit Revenue"
                name="revenueAccount"
                v-model="revenueAccount.name"
                :error="revenueAccountError"
                @input="() => {
                  revenueAccount = {
                    name: revenueAccount.id ? '' : revenueAccount.name,
                    id: null,
                  };
                  revenueAccountError = null;
                }"
              />
            </div>
            <div
              v-if="revenueAccount.name"
              class="col-span-1">
              <Alert
                type="primary-outline"
                icon="heroicons-outline:banknotes"
              >
                {{ moneyUtils.moneyFormatter(revenueAccount.balance) }}
              </Alert>
            </div>
            <div class="col-span-1">
              <ComboboxTextInput
                :field-model-value="liabilityAccount.name ?? ''"
                :suggestions="filteredLiabilityAccountSuggestions.map(makeAccountLegible)"
                :selected-callback="selectLiabilityAccount"
                :allow-new="false"
                :open-by-default="false"
                label="Liability Account"
                type="text"
                placeholder="Liability Account"
                name="liabilityAccount"
                v-model="liabilityAccount.name"
                :error="liabilityAccountError"
                @input="() => {
                  liabilityAccount = {
                    name: liabilityAccount.id ? '' : liabilityAccount.name,
                    id: null,
                  };
                  liabilityAccountError = null;
                }"
              />
            </div>
            <div
              v-if="liabilityAccount.name"
              class="col-span-1">
              <Alert
                type="primary-outline"
                icon="heroicons-outline:banknotes"
              >
                {{ moneyUtils.moneyFormatter(liabilityAccount.balance) }}
              </Alert>
            </div>
          </div>

      </Card>
    </div>
    <div class="col-span-10">
      <Card title="Forfeitable Contracts">
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <ContractsToForfeitTable
              :data="forfeitableContracts"
              :columns="columns"
              :loading="loadingContracts">
              <template v-slot:action="props">
                <div class="grid grid-cols-3 gap-1">
                  <Tooltip placement="top" arrow theme="dark">
                    <template #button>
                      <Button
                        class="btn-primary btn-small"
                        @click="viewContract(props.contractId)"
                      >
                        <Icon icon="heroicons-outline:eye"/>
                      </Button>
                    </template>
                    <span>View</span>
                  </Tooltip>
                  <Tooltip placement="top" arrow theme="dark">
                    <template #button>
                      <Button
                        class="btn-primary btn-small"
                        @click="ignoreContract(props.contractId)"
                        :is-disabled="processing"
                      >
                        <Icon icon="heroicons-outline:clock"/>
                      </Button>
                    </template>
                    <span>Ignore</span>
                  </Tooltip>

                  <Tooltip placement="top" arrow theme="dark">
                    <template #button>
                      <Button
                        class="btn-danger dark:btn-danger"
                        @click="forfeitContract(props.contractId)"
                        :is-disabled="processing"
                      >
                        <Icon icon="heroicons-outline:archive-box-arrow-down"/>
                      </Button>
                    </template>
                    <span>Forfeit</span>
                  </Tooltip>
                </div>
              </template>
            </ContractsToForfeitTable>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
