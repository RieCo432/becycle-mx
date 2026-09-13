<script setup>
import {computed, defineProps} from 'vue';
import Card from '@/components/Card/index.vue';
import ContractSummaryTable from '@/components/Tables/ContractSummaryTable.vue';
import {useRouter} from 'vue-router';

const router = useRouter();

const props = defineProps({
  loading: {
    type: Boolean,
    required: false,
  },
  contracts: {
    type: Array,
    required: false,
  },
  user: {
    type: Object,
    required: false,
  },
});


function viewContract(contractId) {
  const routeData = router.resolve({path: `/contracts/${contractId}`});
  window.open(routeData.href, '_blank');
}

const contractSummaries = computed({
  get: () => {
    return props.contracts
      .map((contract) => {
        const lastDepositTransaction = contract.depositTransactionHeaders
          .toSorted((thA, thB) =>
            new Date(thB.postedOn) - new Date(thA.postedOn))[0];
        let status = 'active';
        if (contract.isDraft) {
          status = 'draft';
        } else if (!lastDepositTransaction) {
          status = 'ERROR';
        } else if (contract.crimeReports.filter((report) => report.closedOn === null).length > 0) {
          status = 'stolen';
        } else if (contract.depositTransactionHeaders.find((th) => th.event === 'deposit_settled')) {
          status = 'closed';
        } else if (contract.depositTransactionHeaders.find((th) => th.event === 'deposit_forfeited')) {
          status = 'forfeited';
        } else if (lastDepositTransaction.event === 'liability_dormant') {
          status = 'dormant';
        } else if (lastDepositTransaction.event === 'liability_reactivated') {
          status = 'active';
        }
        return {
          id: contract.id,
          role: props.user?.id === contract.workingUserId ? 'Mechanic' : 'Safety',
          status: status,
          startDate: contract.startDate,
          endDate: contract.endDate,
          returnedDate: contract.returnedDate,
          firstName: contract.client.firstName,
          lastName: contract.client.lastName,
          bikeMake: contract.bike.make,
          bikeModel: contract.bike.model,
        };
      })
      .sort((a, b) => {
        return new Date(b.startDate) - new Date(a.startDate);
      });
  },
});

const contractColumns = [
  {
    label: 'Status',
    field: 'status',
  },
  {
    label: 'Role',
    field: 'role',
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
    label: 'Returned Date',
    field: 'returnedDate',
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
    label: 'Make',
    field: 'bikeMake',
  },
  {
    label: 'Model',
    field: 'bikeModel',
  },
  {
    label: 'Action',
    field: 'action',
  },
];

const contractActions = [
  {
    name: 'View',
    icon: 'heroicons-outline:eye',
  },
];

</script>

<template>
  <Card
    title="Contracts"
    class-name="rounded-3xl"
  >
    <ContractSummaryTable
      :loading="loading"
      :view-contract="viewContract"
      :actions="contractActions"
      :columns="contractColumns"
      :advanced-table="contractSummaries"/>
  </Card>

</template>

<style scoped lang="scss">

</style>
