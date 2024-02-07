<script>
import clientView from '@/views/client/clientView.vue';
import requests from '@/requests';
export default {
  name: 'clientIndex',
  components: {
    clientView,
  },
  data() {
    return {
      contracts: [],
      client: {},
      contractSummaries: [],
    };
  },

  async created() {
    this.client = (await requests.getClient(this.$route.params.clientId)).data;
    this.contracts = (await requests.getClientContracts(this.client.id, true, true, true)).data;

    this.contractSummaries = (await Promise.all(this.contracts.map(async (contract) => {
      const bike = (await requests.getBike(contract.bikeId)).data;
      let status = 'open';
      if (contract.returnedDate != null) {
        status = 'closed';
      } else {
        if (new Date(contract.endDate).getTime() < new Date().getTime()) {
          status = 'expired';
        }
      }
      return {
        id: contract.id,
        startDate: contract.startDate,
        endDate: contract.endDate,
        returnedDate: contract.returnedDate,
        bikeMake: bike['make'],
        bikeModel: bike.model,
        bikeColour: bike.colour,
        bikeDecals: bike.decals,
        bikeSerialNumber: bike.serialNumber,
        status: status,
      };
    })));
  },
};
</script>

<template>
  <div>
    <client-view :client="client" :contract-summaries="contractSummaries"></client-view>
  </div>
</template>

<style scoped lang="scss">

</style>
