<script>
import requests from '@/requests';
import viewContract from '@/views/contract/viewContract.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

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
      depositCollectingUser: {
        username: 'null',
      },
      workingUser: {
        username: 'null',
      },
      checkingUser: {
        username: 'null',
      },
      contractId: this.$route.params.contractId,
      depositBearers: [],
      activeUsers: [],
      depositReturnedByUser: {
        username: 'null',
      },
      returnAcceptedByUser: {
        username: 'null',
      },
      loadingBike: true,
      loadingClient: true,
      loadingContract: true,
    };
  },
  methods: {
    patchContractReturn(depositAmountReturned, depositReturningUser, depositReturningPassword, returnAcceptingUser, returnAcceptingPasswordOrPin) {
      requests.patchReturnContract(this.contract.id, depositAmountReturned,
          depositReturningUser, depositReturningPassword,
          returnAcceptingUser, returnAcceptingPasswordOrPin).then((response) => {
        toast.success('Contract Returned!', {timeout: 1000});
        this.contract = response.data;
        this.loadReturnUserDetails();
      });
    },
    patchContractExtend() {
      requests.patchExtendContract(this.contract.id).then((response) => {
        toast.success('Contract Extended!', {timeout: 1000});
        this.contract = response.data;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    loadReturnUserDetails() {
      requests.getUser(this.contract['returnAcceptingUserId']).then((response) => {
        this.returnAcceptedByUser = response.data;
      });
      requests.getUser(this.contract['depositReturningUserId']).then((response) => {
        this.depositReturnedByUser = response.data;
      });
    },
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
      if (this.contract.returnedDate != null) {
       this.loadReturnUserDetails();
      }
      Promise.all([
        requests.getUser(this.contract['depositCollectingUserId']),
        requests.getUser(this.contract['workingUserId']),
        requests.getUser(this.contract['checkingUserId']),
      ]).then(([
          depositCollectingUserResponse,
          workingUserResponse,
          checkingUserResponse,
      ]) => {
        this.depositCollectingUser = depositCollectingUserResponse.data;
        this.workingUser = workingUserResponse.data;
        this.checkingUser = checkingUserResponse.data;
        this.loadingContract = false;
      });
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
  <view-contract
      :client="client"
      :bike="bike"
      :deposit-collecting-username="depositCollectingUser.username"
      :working-username="workingUser.username"
      :checking-username="checkingUser.username"
      :contract="contract"
      :deposit-returned-by-username="depositReturnedByUser ? depositReturnedByUser.username : null"
      :return-accepted-by-username="returnAcceptedByUser ? returnAcceptedByUser.username : null"
      :deposit-bearers="depositBearers"
      :active-users="activeUsers"
      :loading-client="loadingClient"
      :loading-bike="loadingBike"
      :loading-contract="loadingContract"
      :patch-contract-extend="patchContractExtend"
      :patch-contract-return="patchContractReturn"
  ></view-contract>
</template>

<style scoped lang="scss">

</style>
