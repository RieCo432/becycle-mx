<script>
import DashButton from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import Tooltip from '@/components/Tooltip/index.vue';

export default {
  name: 'ContractDraftCard',
  components: {Tooltip, Card, DashButton},
  props: {
    continueDraftFunction: {
      type: Function,
      default: () => {},
    },
    draft: {
      type: Object,
      required: true
    },
  }
};
</script>

<template>
  <Card class-name="border border-solid dark:border-slate-600 border-l-2 border-t-2 shadow-lg dark:shadow-slate-900 h-full w-full">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-2">
      <div class="col-span-1">
        <span class="block part-label">Client</span>
        <span class="block part-text">
          {{draft.client !== null ? `${draft.client.firstName} ${draft.client.lastName}` : '-'}}
          <br>
          {{draft.client !== null ? draft.client.emailAddress : '-'}}
        </span>
      </div>
      <div class="col-span-1">
        <span class="block part-label">Bike</span>
        <span class="block part-text">{{draft.bike !== null ? `${draft.bike.make} ${draft.bike.model}` : '-'}}</span>
        <template
            v-if="draft.bike !== null && draft.bike.colours.length > 0">
          <div :class="`w-full rounded-full overflow-hidden grid grid-cols-${draft.bike.colours.length}`">
            <template
                v-for="c in draft.bike.colours"
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
        <span class="block part-text">{{draft.bike !== null ? `${draft.bike.decals !== null ? draft.bike.decals : '-'}` : '-'}}</span>
        <span class="block part-text">{{draft.bike !== null ? `${draft.bike.serialNumber}` : '-'}}</span>
      </div>
      <div class="col-span-1">
        <span class="block part-label">Deposit Collector</span>
        <span class="block part-text">
          {{draft.depositCollectingUser !== null ? `${draft.depositCollectingUser.username} &#163;${draft.depositAmountCollected}` : '-'}}
        </span>
      </div>
      <div class="col-span-1">
        <span class="block part-label">Working Volunteer</span>
        <span class="block part-text">
          {{draft.workingUser !== null ? draft.workingUser.username : '-'}}
        </span>
      </div>
      <div class="col-span-1">
        <span class="block part-label">Checking Volunteer</span>
        <span class="block part-text">
          {{draft.checkingUser !== null ? draft.checkingUser.username : '-'}}
        </span>
      </div>
      <div class="col-span-full">
        <DashButton
            class='w-full h-full'
            @click="() => continueDraftFunction(draft.id)">
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