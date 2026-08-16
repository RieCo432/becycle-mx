<script>
import Card from '@/components/Card/index.vue';
import Tooltip from '@/components/Tooltip/index.vue';
import TextLabelWithPillBadgeIndicatingMatch from '@/components/Card/TextLabelWithPillBadgeIndicatingMatch.vue';
import requests from '@/requests';
import DashButton from '@/components/Button/index.vue';
import Badge from '@/components/Badge/index.vue';

export default {
  name: 'BikeOverviewCard',
  components: {Badge, DashButton, TextLabelWithPillBadgeIndicatingMatch, Tooltip, Card},
  props: {
    bike: {
      type: Object,
      required: true,
    },
    bikeSearch: {
      type: Object,
      required: false,
      default: null,
    },
    noTitle: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      loadedPhotos: false,
      photoUrls: [],
    };
  },
  methods: {
    getContractPhoto(contractId, photoId) {
      requests.getContractPhotoUrl(contractId, photoId)
        .then((response) => {
          this.photoUrls.push(
            {
              id: photoId,
              contractId: contractId,
              url: window.URL.createObjectURL(new Blob([response.data], {type: response.headers['content-type']})),
            });
        });
    },
    getContractPhotos(contractId) {
      requests.getContractPhotoIds(contractId)
        .then((response) => {
          for (const photoId of response.data) {
            if (!this.photoUrls.some((photoUrl) => photoUrl.id === photoId)) {
              this.getContractPhoto(contractId, photoId);
            }
          }
        });
    },
    getAllBikePhotos() {
      if (this.bike) {
        requests.getBikeContracts(this.bike.id, true, true, true, true)
          .then((response) => {
            response.data.forEach((contract) => {
              this.getContractPhotos(contract.id);
            });
          });
      }
    },
    deleteContractPhoto(contractId, photoId) {
      if (confirm('Are you sure you want to delete this photo?')) {
        requests.deleteContractPhoto(contractId, photoId).then((response) => {
          toast.success('Contract photo deleted successfully', {timeout: 2000});
          this.photoUrls.splice(this.photoUrls.findIndex((photoUrl) => photoUrl.id === photoId), 1);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
      }
    },
    openPhoto(url) {
      window.open(url, '_blank');
    },
  },
  mounted() {
    this.getAllBikePhotos();
  },
  watch: {
    bike(newValue) {
      if (newValue) {
        this.getAllBikePhotos();
      }
    },
  },
};
</script>

<template>
  <Card
      :title="noTitle ? '' : 'Bike To Be Matched'"
      class-name="border border-solid dark:border-slate-600 border-l-2 border-t-2 shadow-lg dark:shadow-slate-900 h-full">
    <template v-if="bike">
      <div class="grid grid-cols-4 h-full gap-5">
        <div class="col-span-2">
          <TextLabelWithPillBadgeIndicatingMatch
              :field-data="bike.make"
              :search-data="bikeSearch ? bikeSearch.make : bike.make"
              field-name="Make"/>
        </div>
        <div class="col-span-2">
          <TextLabelWithPillBadgeIndicatingMatch
              :field-data="bike.model"
              :search-data="bikeSearch ? bikeSearch.model : bike.model"
              field-name="Model"/>
        </div>
        <div class="col-span-2">
          <TextLabelWithPillBadgeIndicatingMatch
              :field-data="bike.serialNumber"
              :search-data="bikeSearch ? bikeSearch.serialNumber : bike.serialNumber"
              field-name="Serial Number"/>
        </div>
        <div class="col-span-2">
          <TextLabelWithPillBadgeIndicatingMatch
              :field-data="bike.decals && bike.decals !== '' ? bike.decals : null"
              :search-data="bikeSearch ? (bikeSearch.decals && bikeSearch.decals !== '' ? bikeSearch.decals : null) : bike.decals && bike.decals !== '' ? bike.decals : null"
              field-name="Decals"/>
        </div>
        <div class="col-span-2">
          <TextLabelWithPillBadgeIndicatingMatch
            :field-data="bike.disposition"
            :search-data="bike.disposition"
            field-name="Disposition"/>
        </div>
        <div class="col-span-2">
          <TextLabelWithPillBadgeIndicatingMatch
            :field-data="bike.roughValue ? `£ ${(bike.roughValue / 100)?.toFixed(2)}` : 'n/a'"
            :search-data="bike.roughValue ? `£ ${(bike.roughValue / 100)?.toFixed(2)}` : 'n/a'"
            field-name="Rough Value"/>
        </div>
        <div class="col-span-4">
          <TextLabelWithPillBadgeIndicatingMatch
              :search-data="bikeSearch ? bikeSearch.colours?.map((c) => c.hex) : bike.colours?.map((c) => c.hex)"
              :field-data="bike.colours?.map((c) => c.hex)"
              field-name="Colours">
            <div class="mt-2 h-10 rounded-full overflow-hidden">
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
        <div class="col-span-full">
          <Badge
            label="Photos"
            badgeClass="bg-opacity-[0.12] pill bg-primary-500 text-primary-500"
          />
          <div class="mt-2 grid grid-cols-12 gap-5">
            <div v-for="photoUrl in photoUrls" class="col-span-4 lg:col-span-3 min-h-full" :key="photoUrl.id">
              <div class="w-full h-auto rounded-md">
                <img :src="photoUrl.url" alt="Photo" class="w-full h-full" @click="() => openPhoto(photoUrl.url)"/>
              </div>
            </div>
          </div>
        </div>
        <div class="col-span-4">
          <slot name="footer"/>
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
