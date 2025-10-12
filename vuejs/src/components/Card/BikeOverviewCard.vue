<script>
import Card from '@/components/Card/index.vue';
import Tooltip from '@/components/Tooltip/index.vue';
import TextLabelWithPillBadgeIndicatingMatch from '@/components/Card/TextLabelWithPillBadgeIndicatingMatch.vue';

export default {
  name: 'BikeOverviewCard',
  components: {TextLabelWithPillBadgeIndicatingMatch, Tooltip, Card},
  props: {
    bike: {
      type: Object,
      required: true,
    },
    bikeSearch: {
      type: Object,
      required: false,
      default: () => {},
    },
  },
};
</script>

<template>
  <Card
      title="Bike To Be Matched"
      class-name="border border-solid dark:border-slate-600 border-l-2 border-t-2 shadow-lg dark:shadow-slate-900 h-full">
    <template v-if="bike">
      <div class="grid grid-cols-4 h-full gap-5">
        <div class="col-span-2">
          <TextLabelWithPillBadgeIndicatingMatch
              :field-data="bike.make"
              :search-data="bikeSearch.make"
              field-name="Make"/>
        </div>
        <div class="col-span-2">
          <TextLabelWithPillBadgeIndicatingMatch
              :field-data="bike.model"
              :search-data="bikeSearch.model"
              field-name="Model"/>
        </div>
        <div class="col-span-2">
          <TextLabelWithPillBadgeIndicatingMatch
              :field-data="bike.serialNumber"
              :search-data="bikeSearch.serialNumber"
              field-name="Serial Number"/>
        </div>
        <div class="col-span-2">
          <TextLabelWithPillBadgeIndicatingMatch
              :field-data="bike.decals && bike.decals !== '' ? bike.decals : null"
              :search-data="bikeSearch.decals && bikeSearch.decals !== '' ? bikeSearch.decals : null"
              field-name="Decals"/>
        </div>
        <div class="col-span-4">
          <TextLabelWithPillBadgeIndicatingMatch
              :search-data="bikeSearch.colours.map((c) => c.hex)"
              :field-data="bike.colours.map((c) => c.hex)"
              field-name="Colours">
            <div class="h-10 rounded-full overflow-hidden">
              <div :class="`w-full h-full rounded-full overflow-hidden grid grid-cols-${bike.colours.length}`">
                <template
                    v-for="c in bike.colours"
                    :key="c.name"
                >
                  <Tooltip placement="top" arrow theme="dark" btn-class="col-span-1" :btn-style="{backgroundColor: c.hex}">
                    <template #button>
                      <div class="w-full h-full"></div>
                    </template>
                    <span>{{ c.name }} ({{ c.hex }})</span>
                  </Tooltip>
                </template>
              </div>
            </div>
          </TextLabelWithPillBadgeIndicatingMatch>
        </div>
        <!--            <div class="col-span-4 col-start-1 mt-auto">-->
        <!--              <DashButton class="w-full" :is-disabled="isInWriteMode" @click="writeBikeDetailsToNfcTag">-->
        <!--                Write To NFC Tag-->
        <!--              </DashButton>-->
        <!--            </div>-->
      </div>
    </template>
    <template v-else>
      <div class="h-full w-full flex items-center justify-center">
        New Bike will be added
      </div>
    </template>
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
