<script>
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Card from '@/components/Card';
import PotentialClientDuplicatesAccordion from '@/components/Accordion/ClientDuplicates.vue';
import Button from '@/components/Button/index.vue';

const toast = useToast();

export default {
  name: 'manageDuplicateClients',
  components: {
    Card,
    PotentialClientDuplicatesAccordion,
    Button,
  },
  data() {
    return {
      potentialDuplicateClients: null,
    };
  },
  computed: {
    potentialDuplicateClientsIgnored() {
      return this.potentialDuplicateClients.filter((i) => i.ignore);
    },
    potentialDuplicateClientsNotIgnored() {
      return this.potentialDuplicateClients.filter((i) => !i.ignore);
    },
  },
  methods: {
    getPotentialDuplicateClients() {
      requests.getPotentialDuplicateClients().then((response) => {
        this.potentialDuplicateClients = response.data;
        this.potentialDuplicateClients.sort((a, b) => (b.similarityScore - a.similarityScore));
      });
    },
    refreshPotentialDuplicateClients() {
      requests.refreshPotentialDuplicateClients().then(() => {
        toast.success('This action might take a few minutes to complete.');
      });
    },
    handleIgnore(clientDuplicate) {
      const indexInArray = this.potentialDuplicateClients.findIndex((a) => (a.id === clientDuplicate.id));
      this.potentialDuplicateClients.splice(indexInArray, 1, clientDuplicate);
      toast.warning('Duplicate Ignored', {timeout: 2000});
    },
    handleResolve(clientDuplicateId) {
      const indexInArray = this.potentialDuplicateClients.findIndex((a) => (a.id === clientDuplicateId));
      this.potentialDuplicateClients.splice(indexInArray, 1);
      toast.success('Duplicate Resolved', {timeout: 2000});
    },
  },
  created() {
    this.getPotentialDuplicateClients();
  },
};
</script>

<template>
  <div class="grid grid-cols-1 gap-5">
    <div class="col-span-1">
      <Card title="Potential Duplicates To Be Checked">
        <template #header>
          <Button @click="refreshPotentialDuplicateClients">Search For Duplicates</Button>
        </template>
        <PotentialClientDuplicatesAccordion
            v-if="potentialDuplicateClients !== null"
            :items="potentialDuplicateClientsNotIgnored.slice(0, 20)"
            @potential-client-duplicate-ignored="handleIgnore"
            @potential-client-duplicate-resolved="handleResolve"
        />
      </Card>
    </div>
    <div class="col-span-1">
      <Card title="Potential Duplicates Ignored">
        <PotentialClientDuplicatesAccordion
            v-if="potentialDuplicateClients !== null"
            :items="potentialDuplicateClientsIgnored"
            @potential-client-duplicate-ignored="handleIgnore"
            @potential-client-duplicate-resolved="handleResolve"
        />
      </Card>
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>
