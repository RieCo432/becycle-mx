<script>
import DashButton from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';

export default {
  name: 'ContractDraftCard',
  components: {Card, DashButton},
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
        <span class="block part-text">
          {{draft.bike !== null ? `${draft.bike.make} ${draft.bike.model}` : '-'}}
          <br>
          {{draft.bike !== null ? `${draft.bike.colour} ${draft.bike.decals !== null ? draft.bike.decals : ''}` : '-'}}
          <br>
          {{draft.bike !== null ? `${draft.bike.serialNumber}` : '-'}}
        </span>
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