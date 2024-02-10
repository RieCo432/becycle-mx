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
    };
  },
  async mounted() {
    this.contract = (await requests.getMyContract(this.$route.params.contractId)).data;

    this.workingUsername = this.contract['workingUsername'];
    this.checkingUsername = this.contract['checkingUsername'];
    this.depositCollectingUsername = this.contract['depositCollectingUsername'];
    this.returnAcceptedByUsername = this.contract['returnAcceptingUsername'];
    this.depositReturnedByUsername = this.contract['depositReturningUsername'];

    requests.getBike(this.contract.bikeId).then((response) => {
      this.bike = response.data;
    });
    requests.getClientMe().then((response) => {
      this.client = response.data;
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
  ></view-contract>
</template>

<style scoped lang="scss">

</style>
