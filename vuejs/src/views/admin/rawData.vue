<script>
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import requests from '@/requests';
import ContractEditTable from '@/components/Tables/ContractEditTable.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'rawData',
  components: {ContractEditTable, DashButton, Card},
  data() {
    return {
      loadingContracts: true,
      rawContractData: [],
      columns: [
        {
          label: 'Client ID',
          field: 'clientId',
        },
        {
          label: 'Bike ID',
          field: 'bikeId',
        },
        {
          label: 'Deposit Collected',
          field: 'depositAmountCollected',
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
          label: 'Contract Type',
          field: 'contractType',
        },
        {
          label: 'Date Returned',
          field: 'returnedDate',
        },
        {
          label: 'Deposit Returned',
          field: 'depositAmountReturned',
        },
        {
          label: 'Working Volunteer ID',
          field: 'workingUserId',
        },
        {
          label: 'Checking Volunteer ID',
          field: 'checkingUserId',
        },
        {
          label: 'Return Received By',
          field: 'returnAcceptingUserId',
        },
        {
          label: 'Action',
          field: 'action',
        },
      ],
      actions: [
        {
          label: 'View Contract',
          id: 'view',
          icon: 'heroicons-outline:eye',
          func: (contractId) => {
            this.viewContract(contractId);
          },
        },
        {
          label: 'Delete Contract',
          id: 'delete',
          icon: 'heroicons-outline:trash',
          func: (contractId) => {
            requests.deleteContract(contractId).then(() => {
              toast.success('Contract Deleted!', {timeout: 2000});
              const indexInArray = this.rawContractData.findIndex((c) => c.id === contractId);
              this.rawContractData.splice(indexInArray, 1);
            });
          },
        },
      ],
    };
  },
  methods: {
    downloadRawDataExcel() {
      requests.downloadRawDataExcel().then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'contracts.xlsx');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      });
    },
    downloadRawDataPdf() {
      requests.downloadRawDataPdf().then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'contracts.pdf');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      });
    },
    viewContract(contractId) {
      this.$router.push({path: `/contracts/${contractId}`});
    },
    getContracts() {
      this.loadingContracts = true;
      requests.getContracts().then((response) => {
        this.rawContractData = response.data;
        this.loadingContracts = false;
      });
    },
  },
  created() {
    this.getContracts();
  },
};
</script>

<template>
  <div class="grid grid-cols-1">
    <div class="col-span-1">
      <Card title="Raw Data Access">
        <template #header>
          <DashButton @click="downloadRawDataPdf">Download PDF</DashButton>
          <DashButton @click="downloadRawDataExcel" class="ml-5">Download Excel</DashButton>
        </template>
        <div>
          <ContractEditTable
              title="Edit Contract Data"
              :loading="loadingContracts"
              :actions="actions"
              :columns="columns"
              :advanced-table="rawContractData"></ContractEditTable>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
