<script>
import DashButton from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import Tooltip from '@/components/Tooltip/index.vue';
import TransactionLinesTable from '@/components/Tables/TransactionLinesTable.vue';
import requests from '@/requests';

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
  data() {
    return {
      photoUrls: [],
      loadingContractPhotos: true,
    };
  },
  methods: {
    getContractPhoto(photoId) {
      requests.getContractPhotoUrl(this.contract.id, photoId)
        .then((response) => {
          this.photoUrls.push(
            {
              id: photoId,
              url: window.URL.createObjectURL(new Blob([response.data], {type: response.headers['content-type']})),
            });
        });
    },
    getContractPhotos() {
      this.loadingContractPhotos = true;
      requests.getContractPhotoIds(this.contract.id)
        .then((response) => {
          for (const photoId of response.data) {
            this.getContractPhoto(photoId);
          }
          this.loadingContractPhotos = false;
        });
    },
    openPhoto(url) {
      window.open(url, '_blank');
    },
  },
  mounted() {
    this.getContractPhotos();
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
                  <div class="w-full h-5"/>
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
      <div class="col-span-full" v-if="!loadingContractPhotos">
        <span class="block part-label">Photos</span>
        <div class="block part-text">
          <div class="grid grid-cols-8 gap-5">
            <div v-for="photoUrl in photoUrls" class="col-span-4 lg:col-span-2 min-h-full" :key="photoUrl.id">
              <img :src="photoUrl.url" alt="Photo" class="w-full h-full" @click="() => openPhoto(photoUrl.url)"/>
            </div>
          </div>
        </div>
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
