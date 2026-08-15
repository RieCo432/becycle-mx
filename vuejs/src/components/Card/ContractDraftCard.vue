<script>
import DashButton from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import Tooltip from '@/components/Tooltip/index.vue';
import TransactionLinesTable from '@/components/Tables/TransactionLinesTable.vue';

export default {
  name: 'ContractDraftCard',
  components: {TransactionLinesTable, Tooltip, Card, DashButton},
  props: {
    selectContractFunction: {
      type: Function,
      default: () => {},
    },
    contract: {
      type: Object,
      required: true,
    },
  },
};
</script>

<template>
  <Card class-name="border border-solid dark:border-slate-600 border-l-2 border-t-2 shadow-lg dark:shadow-slate-900 h-full w-full">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-2">
      <div class="col-span-1">
        <span class="block part-label">Client</span>
        <span class="block part-text">
          {{ contract.client ? `${contract.client.firstName} ${contract.client.lastName}` : '-' }}
          <br>
          {{ contract.client ? contract.client.emailAddress : '-' }}
        </span>
      </div>
      <div class="col-span-1">
        <span class="block part-label">Bike</span>
        <span class="block part-text">{{ contract.bike ? `${contract.bike.make} ${contract.bike.model}` : '-' }}</span>
        <template
            v-if="contract.bike && contract.bike.colours.length > 0">
          <div :class="`w-full rounded-full overflow-hidden grid grid-cols-${contract.bike.colours.length}`">
            <template
                v-for="c in contract.bike.colours"
                :key="c.name"
            >
              <Tooltip placement="top" arrow theme="dark" btn-class="col-span-1" :btn-style="{backgroundColor: c.hex}">
                <template #button>
                  <div class="w-full h-5"></div>
                </template>
                <span>{{ c.name }} ({{ c.hex }})</span>
              </Tooltip>
            </template>
          </div>
        </template>
        <template v-else>
          <span class="block part-text">-</span>
        </template>
        <span class="block part-text">{{ contract.bike ? `${contract.bike.decals !== null ? contract.bike.decals : '-'}` : '-' }}</span>
        <span class="block part-text">{{ contract.bike ? `${contract.bike.serialNumber}` : '-' }}</span>
      </div>
      <div class="col-span-1">
        <span class="block part-label">Contract Type</span>
        <span class="block part-text">
          {{ contract.contractType ?? '-' }}
        </span>
      </div>
      <div class="col-span-1">
        <span class="block part-label">Bike Condition</span>
        <span class="block part-text">
          {{ contract.conditionOfBike ?? '-' }}
        </span>
      </div>

      <div class="col-span-1">
        <span class="block part-label">Notes</span>
        <span class="block part-text">
          {{ contract.notes ?? '-' }}
        </span>
      </div>

      <div class="col-span-1">
        <span class="block part-label">Working Volunteer</span>
        <span class="block part-text">
          {{ contract.workingUser ? contract.workingUser.username : '-' }}
        </span>
      </div>
      <div class="col-span-1">
        <span class="block part-label">Checking Volunteer</span>
        <span class="block part-text">
          {{ contract.checkingUser ? contract.checkingUser.username : '-' }}
        </span>
      </div>
      <div class="col-span-1">
        <span class="block part-label">Deposit</span>
        <TransactionLinesTable
          v-if="contract.depositTransactionHeaders.length > 0"
          :transaction-header="contract.depositTransactionHeaders.find(th => th.event === 'deposit_collected')"/>
        <p v-else class="text-slate-600 dark:text-slate-300">-</p>
      </div>
      <div class="col-span-full">
        <DashButton
            class='w-full h-full'
            @click="() => selectContractFunction(contract.id)">
          Continue
        </DashButton>
      </div>
    </div>
  </Card>
</template>

<style scoped lang="scss">
.part-label {
  @apply text-base text-slate-400 dark:text-slate-400 mb-1;
}
.part-text {
  @apply text-base text-slate-600 dark:text-slate-300 font-medium;
}

</style>
