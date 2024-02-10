<script>
import requests from '@/requests';
import viewContract from '@/views/contract/viewContract.vue';


export default {
  name: 'clientContractIndex',
  components: {
    viewContract,
  },
  data() {
    return {
      client: {},
      bike: {},
      contract: {},
      depositCollectingUsername: null,
      workingUsername: null,
      checkingUsername: null,
      contractId: this.$route.params.contractId,
      depositReturnedByUsername: null,
      returnAcceptedByUsername: null,
      loadingBike: true,
      loadingClient: true,
      loadingContract: true,
    };
  },
  mounted() {
    requests.getMyContract(this.$route.params.contractId).then((response) => {
      this.contract = response.data;
      requests.getBike(this.contract.bikeId).then((response) => {
        this.bike = response.data;
        this.loadingBike = false;
      });
      requests.getClientMe().then((response) => {
        this.client = response.data;
        this.loadingClient = false;
      });
      this.workingUsername = this.contract['workingUsername'];
      this.checkingUsername = this.contract['checkingUsername'];
      this.depositCollectingUsername = this.contract['depositCollectingUsername'];
      this.returnAcceptedByUsername = this.contract['returnAcceptingUsername'];
      this.depositReturnedByUsername = this.contract['depositReturningUsername'];
      this.loadingContract = false;
    });
  },
};
</script>

<template>
  <view-contract :client="client"
                 :bike="bike"
                 :depositCollectingUsername="depositCollectingUsername"
                 :workingUsername="workingUsername"
                 :checkingUsername="checkingUsername"
                 :contract="contract"
                 :depositReturnedByUsername="depositReturnedByUsername"
                 :returnAcceptedByUsername="returnAcceptedByUsername"
                 :loading-client="loadingClient"
                 :loading-bike="loadingBike"
                 :loading-contract="loadingContract"
  ></view-contract>
</template>

<style scoped lang="scss">

</style>
