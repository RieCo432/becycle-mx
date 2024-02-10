<script>
import requests from '@/requests';
import viewContract from '@/views/contract/viewContract.vue';


export default {
  name: 'contractIndex',
  components: {
    viewContract,
  },
  data() {
    return {
      client: {},
      bike: {},
      contract: {},
      depositCollectingUser: {},
      workingUser: {},
      checkingUser: {},
      contractId: this.$route.params.contractId,
      depositBearers: [],
      activeUsers: [],
      depositReturnedByUser: {},
      returnAcceptedByUser: {},
      loadingBike: true,
      loadingClient: true,
      loadingContract: true,
    };
  },
  mounted() {
    requests.getContract(this.$route.params.contractId).then((response) => {
      this.contract = response.data;
      requests.getBike(this.contract.bikeId).then((response) => {
        this.bike = response.data;
        this.loadingBike = false;
      });
      requests.getClient(this.contract.clientId).then((response) => {
        this.client = response.data;
        this.loadingClient = false;
      });
      requests.getUser(this.contract['depositCollectingUserId']).then((response) => {
        this.depositCollectingUser = response.data;
      });
      requests.getUser(this.contract['workingUserId']).then((response) => {
        this.workingUser = response.data;
      });
      requests.getUser(this.contract['checkingUserId']).then((response) => {
        this.checkingUser = response.data;
      });
      if (this.contract.returnedDate != null) {
        requests.getUser(this.contract['returnAcceptingUserId']).then((response) => {
          this.returnAcceptedByUser = response.data;
        });
        requests.getUser(this.contract['depositReturningUserId']).then((response) => {
          this.depositReturnedByUser = response.data;
        });
      }
      this.loadingContract = false;
    });
    requests.getDepositBearers().then((response) => {
      this.depositBearers = response.data.map((user) => ({
        label: user.username,
        value: user.username,
      }));
    });
    requests.getActiveUsers().then((response) => {
      this.activeUsers = response.data.map((user) => ({
        label: user.username,
        value: user.username,
      }));
    });
  },
};
</script>

<template>
  <view-contract :client="client"
                 :bike="bike"
                 :depositCollectingUsername="depositCollectingUser.username"
                 :workingUsername="workingUser.username"
                 :checkingUsername="checkingUser.username"
                 :contract="contract"
                 :depositReturnedByUsername="depositReturnedByUser ? depositReturnedByUser.username : null"
                 :returnAcceptedByUsername="returnAcceptedByUser ? returnAcceptedByUser.username : null"
                 :deposit-bearers="depositBearers"
                 :active-users="activeUsers"
                 :loading-client="loadingClient"
                 :loading-bike="loadingBike"
                 :loading-contract="loadingContract"
  ></view-contract>
</template>

<style scoped lang="scss">

</style>
