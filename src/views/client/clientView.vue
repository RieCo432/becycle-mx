<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';

export default {
  name: 'clientView',
  components: {Card},

  data() {
    return {
      client: {
        firstName: null,
        lastName: null,
        emailAddress: null,
        id: null,
      },
      openContracts: [],
      openContractSummaries: [],
      closedContracts: [],
      closedContractSummaries: [],
      expiredContracts: [],
      expiredContractSummaries: [],
    };
  },
  computed: {
    name() {
      return this.client.firstName + ' ' + this.client.lastName;
    },
  },
  async created() {
    this.client = (await requests.getClient(this.$route.query.id)).data;

    this.openContracts = (await requests.getClientContracts(this.$route.query.id, true, false, false)).data;
    this.openContractSummaries = (await Promise.all(this.openContracts.map(async (contract) => {
      return {
        startDate: contract.startDate,
        endDate: contract.endDate,
        bike: (await requests.getBike(contract.bikeId)).data,
      };
    })));

    this.closedContracts = (await requests.getClientContracts(this.$route.query.id, false, true, false)).data;
    this.closedContractSummaries = (await Promise.all(this.closedContracts.map(async (contract) => {
      return {
        startDate: contract.startDate,
        endDate: contract.endDate,
        bike: (await requests.getBike(contract.bikeId)).data,
      };
    })));

    this.expiredContracts = (await requests.getClientContracts(this.$route.query.id, false, false, true)).data;
    this.expiredContractSummaries = (await Promise.all(this.expiredContracts.map(async (contract) => {
      return {
        startDate: contract.startDate,
        endDate: contract.endDate,
        bike: (await requests.getBike(contract.bikeId)).data,
      };
    })));
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="lg:col-span-8 col-span-12">
      <Card :title="name">
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <h4>{{client.emailAddress}}</h4>
          </div>
          <div class="col-span-6">
            <h4>Open Contracts:</h4>
            <ul>
              <li v-for="contract in openContractSummaries">{{contract}}</li>
            </ul>
            <h4>Closed Contracts:</h4>
            <ul>
              <li v-for="contract in closedContractSummaries">{{contract}}</li>
            </ul>
            <h4>Expired Contracts:</h4>
            <ul>
              <li v-for="contract in expiredContractSummaries">{{contract}}</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>
