<script>
import requests from '@/requests';
import viewContract from '@/views/contract/viewContract.vue';
import {useToast} from 'vue-toastification';
import EditClientDetailsModal from '@/components/Modal/EditClientDetailsModal.vue';
import EditBikeDetailsModal from '@/components/Modal/EditBikeDetailsModal.vue';
import EditContractDetailsModal from '@/components/Modal/EditContractDetailsModal.vue';

const toast = useToast();

export default {
  name: 'contractIndex',
  components: {
    EditContractDetailsModal,
    EditBikeDetailsModal,
    EditClientDetailsModal,
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
      showEditClientDetailsModal: false,
      showEditBikeDetailsModal: false,
      showEditContractDetailsModal: false,
      isUserAdmin: false,
    };
  },
  methods: {
    userSortingFunction(user1, user2) {
      if (user1.username.toLowerCase() < user2.username.toLowerCase()) return -1;
      if (user1.username.toLowerCase() > user2.username.toLowerCase()) return 1;
      return 0;
    },
    getContract() {
      this.loadingContract = true;
      this.loadingBike = true;
      this.loadingClient = true;
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
        ]).then(([depositCollectingUserResponse,
          workingUserResponse,
          checkingUserResponse,
        ]) => {
          this.depositCollectingUser = depositCollectingUserResponse.data;
          this.workingUser = workingUserResponse.data;
          this.checkingUser = checkingUserResponse.data;
          this.loadingContract = false;
        });
      });
    },
    patchContractReturn(depositAmountReturned, depositReturningUser, depositReturningPassword,
      returnAcceptingUser, returnAcceptingPasswordOrPin) {
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
    this.getContract();
    requests.getDepositBearers().then((response) => {
      this.depositBearers = response.data.sort(this.userSortingFunction).map((user) => ({
        label: user.username,
        value: user.username,
      }));
    });
    requests.getActiveUsers().then((response) => {
      this.activeUsers = response.data.sort(this.userSortingFunction).map((user) => ({
        label: user.username,
        value: user.username,
      }));
    });
    requests.getUserMe().then((response) => {
      this.isUserAdmin = response.data.admin;
    });
  },
};
</script>

<template>
  <div>
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
        :open-edit-client-details-modal="() => showEditClientDetailsModal = true"
        :open-edit-bike-details-modal="() => showEditBikeDetailsModal = true"
        :go-to-bike="() => this.$router.push({path: `/bikes/${bike.id}`})"
        :is-user="true"
        :is-user-admin="isUserAdmin"
        :open-edit-contract-details-modal="() => showEditContractDetailsModal = true"
    ></view-contract>
    <EditClientDetailsModal v-if="!loadingClient"
                            :close-modal="() => showEditClientDetailsModal = false"
                            :show-modal="showEditClientDetailsModal"
                            :client="client"
                            @client-details-updated="(updatedDetails) => client = updatedDetails"
    ></EditClientDetailsModal>
    <EditBikeDetailsModal v-if="!loadingBike"
                          :close-modal="() => showEditBikeDetailsModal = false"
                          :show-modal="showEditBikeDetailsModal"
                          :bike="bike"
                          @bike-details-updated="(updatedBike) => bike = updatedBike">
    </EditBikeDetailsModal>
    <EditContractDetailsModal v-if="!loadingContract"
                          :close-modal="() => showEditContractDetailsModal = false"
                          :show-modal="showEditContractDetailsModal"
                          :contract="contract"
                          @contract-details-updated="getContract">
    </EditContractDetailsModal>

  </div>
</template>

<style scoped lang="scss">

</style>
