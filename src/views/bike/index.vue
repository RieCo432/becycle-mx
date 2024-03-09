<script>
import Card from '@/components/Card/index.vue';
import ContractSummaryTable from '@/components/Tables/ContractSummaryTable.vue';
import {useCredentialsStore} from '@/store/credentialsStore';
import TableSkeleton from '@/components/Skeleton/TableSkeleton.vue';
import requests from '@/requests';
import DashButton from '@/components/Button/index.vue';
import ContractBikeCardSkeleton from '@/components/Skeleton/ContractBikeCardSkeleton.vue';
import EditBikeDetailsModal from '@/components/Modal/EditBikeDetailsModal.vue';

const credentialsStore = useCredentialsStore();

export default {
  name: 'clientView',
  components: {
    EditBikeDetailsModal,
    ContractBikeCardSkeleton,
    DashButton,
    TableSkeleton,
    Card,
    ContractSummaryTable,
  },
  data() {
    return {
      bike: {},
      contractSummaries: [],
      loadingContracts: true,
      loadingBikeDetails: true,
      showEditBikeDetailsModal: false,
      contractActions: [
        {
          name: 'View',
          icon: 'heroicons-outline:eye',
        }, ...(credentialsStore.isUserLoggedIn() ? [{
          name: 'Return',
          icon: 'heroicons:pencil-square',
        }] : []),
      ],
      contractColumns: [
        {
          label: 'Status',
          field: 'status',
        },
        {
          label: 'Start Date',
          field: 'startDate',
        },
        {
          label: 'End Date',
          field: 'endDate',
        },
        {
          label: 'First Name',
          field: 'firstName',
        },
        {
          label: 'Last Name',
          field: 'lastName',
        },

        {
          label: 'Email Address',
          field: 'emailAddress',
        },
        {
          label: 'Action',
          field: 'action',
        },
      ],
    };
  },
  created() {
    requests.getBike(this.$route.params.bikeId).then((response) => {
      this.bike = response.data;
      this.loadingBikeDetails = false;
    });
    requests.getBikeContracts(this.$route.params.bikeId, true, true, true).then((response) => {
      Promise.all(response.data.map((contract) => {
        return requests.getClient(contract.clientId).then((clientResponse) => ({
          id: contract.id,
          status: 'open',
          startDate: contract.startDate,
          endDate: contract.endDate,
          firstName: clientResponse.data.firstName,
          lastName: clientResponse.data.lastName,
          emailAddress: clientResponse.data.emailAddress,
        }));
      })).then((contractSummaries) => {
        this.contractSummaries = contractSummaries;
        this.loadingContracts = false;
      });
    });
  },
  computed: {
    name() {
      return this.client.firstName + ' ' + this.client.lastName;
    },
  },
  methods: {
    viewContract(contractId) {
      this.$router.push({path: `/contracts/${contractId}`});
    },
    openEditBikeDetailsModal() {
      this.showEditBikeDetailsModal = true;
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">

      <Card title="Details">
        <ContractBikeCardSkeleton v-if="loadingBikeDetails"></ContractBikeCardSkeleton>
        <template v-else>
          <div class="grid grid-cols-12 h-full gap-5">
            <div class="col-span-12" >
              <p class="text-slate-600 dark:text-slate-300">{{bike.make}} {{bike.model}}</p>
              <p class="text-slate-600 dark:text-slate-300">{{bike.colour}} {{bike.decals}}</p>
              <p class="text-slate-600 dark:text-slate-300">{{bike.serialNumber}}</p>
            </div>
            <div class="col-span-6 mt-auto">
              <DashButton class="w-full" @click="openEditBikeDetailsModal">
                Edit Details
              </DashButton>
            </div>
          </div>
        </template>
      </Card>
    </div>
    <div class="col-span-12">
      <Card>
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <ContractSummaryTable
                :loading="loadingContracts"
                :actions="contractActions"
                :columns="contractColumns"
                :advanced-table="contractSummaries"
                title="Contracts"
                :view-contract="viewContract">
            </ContractSummaryTable>
          </div>
        </div>
      </Card>
    </div>
    <EditBikeDetailsModal v-if="!loadingBikeDetails"
                          :close-modal="() => showEditBikeDetailsModal = false"
                          :show-modal="showEditBikeDetailsModal"
                          :bike="bike"
                          @bike-details-updated="(updatedBike) => bike = updatedBike">
    </EditBikeDetailsModal>
  </div>

</template>

<style scoped lang="scss">

</style>
