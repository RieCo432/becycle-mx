<script>
import requests from '@/requests';
import viewContract from '@/views/contract/viewContract.vue';
import EditMyDetailsModal from '@/components/Modal/EditMyDetailsModal.vue';


export default {
  name: 'clientContractIndex',
  components: {
    EditMyDetailsModal,
    viewContract,
  },
  data() {
    return {
      client: {},
      bike: {},
      contract: {},
      contractId: this.$route.params.contractId,
      loadingBike: true,
      loadingClient: true,
      loadingContract: true,
      showEditClientDetailsModal: false,
    };
  },
  mounted() {
    requests.getMyContract(this.$route.params.contractId).then((response) => {
      this.contract = response.data;
      requests.getClientBike(this.contract.bikeId).then((response) => {
        this.bike = response.data;
        this.loadingBike = false;
      });
      requests.getClientMe().then((response) => {
        this.client = response.data;
        this.loadingClient = false;
      });
      this.loadingContract = false;
    });
  },
};
</script>

<template>
  <div>
    <view-contract :client="client"
                   :bike="bike"
                   :contract="contract"
                   :loading-client="loadingClient"
                   :loading-bike="loadingBike"
                   :loading-contract="loadingContract"
                   :open-edit-client-details-modal="() => showEditClientDetailsModal = true"
                   :is-user="false"
    ></view-contract>
    <EditMyDetailsModal v-if="!loadingClient"
                        :show-modal="showEditClientDetailsModal"
                        :client="client"
                        :close-modal="() => showEditClientDetailsModal = false"
                        @client-details-updated="(updatedDetails) => client = updatedDetails">
    </EditMyDetailsModal>
  </div>

</template>

<style scoped lang="scss">

</style>
