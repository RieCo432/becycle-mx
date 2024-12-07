<script>
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Card from '@/components/Card';
import PotentialBikeDuplicatesAccordion from '@/components/Accordion/BikeDuplicates.vue';
import Button from '@/components/Button/index.vue';

const toast = useToast();

export default {
  name: 'manageDuplicateClients',
  components: {
    Card,
    PotentialBikeDuplicatesAccordion,
    Button,
  },
  data() {
    return {
      potentialDuplicateBikes: null,
    };
  },
  computed: {
    potentialDuplicateBikesIgnored() {
      return this.potentialDuplicateBikes.filter((i) => i.ignore);
    },
    potentialDuplicateBikesNotIgnored() {
      return this.potentialDuplicateBikes.filter((i) => !i.ignore);
    },
  },
  methods: {
    getPotentialDuplicateBikes() {
      requests.getPotentialDuplicateBikes().then((response) => {
        this.potentialDuplicateBikes = response.data;
        this.potentialDuplicateBikes.sort((a, b) => (b.similarityScore - a.similarityScore));
      });
    },
    refreshPotentialDuplicateBikes() {
      requests.refreshPotentialDuplicateBikes().then(() => {
        toast.success('This action might take a few minutes to complete.');
      });
    },
    handleIgnore(bikeDuplicate) {
      const indexInArray = this.potentialDuplicateBikes.findIndex((a) => (a.id === bikeDuplicate.id));
      this.potentialDuplicateBikes.splice(indexInArray, 1, bikeDuplicate);
      toast.warning('Duplicate Ignored', {timeout: 2000});
    },
    handleResolve(bikeDuplicateId) {
      const indexInArray = this.potentialDuplicateBikes.findIndex((a) => (a.id === bikeDuplicateId));
      this.potentialDuplicateBikes.splice(indexInArray, 1);
      toast.success('Duplicate Resolved', {timeout: 2000});
    },
  },
  created() {
    this.getPotentialDuplicateBikes();
  },
};
</script>

<template>
  <div class="grid grid-cols-1 gap-5">
    <div class="col-span-1">
      <Card title="Potential Duplicates To Be Checked">
        <template #header>
          <Button @click="refreshPotentialDuplicateBikes">Search For Duplicates</Button>
        </template>
        <PotentialBikeDuplicatesAccordion
            v-if="potentialDuplicateBikes !== null"
            :items="potentialDuplicateBikesNotIgnored.slice(0, 20)"
            @potential-bike-duplicate-ignored="handleIgnore"
            @potential-bike-duplicate-resolved="handleResolve"
        />
      </Card>
    </div>
    <div class="col-span-1">
      <Card title="Potential Duplicates Ignored">
        <PotentialBikeDuplicatesAccordion
            v-if="potentialDuplicateBikes !== null"
            :items="potentialDuplicateBikesIgnored"
            @potential-bike-duplicate-ignored="handleIgnore"
            @potential-bike-duplicate-resolved="handleResolve"
        />
      </Card>
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>
