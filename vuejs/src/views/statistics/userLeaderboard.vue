<script>
import AdvancedTable from '@/components/Tables/AdvancedTable.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';

export default {
  name: 'userLeaderboard',
  components: {Card, AdvancedTable},
  data() {
    return {
      loading: true,
      leaderboard: [],
      columns: [
        {
          field: 'username',
          label: 'Username',
        },
        {
          field: 'contractsDone',
          label: 'Bikes Rented',
          type: 'number',
        },
        {
          field: 'contractsChecked',
          label: 'Bikes Checked',
          type: 'number',
        },
        {
          field: 'contractsReturned',
          label: 'Returns Accepted',
          type: 'number',
        },
        {
          field: 'depositsCollected',
          label: 'Deposits Collected',
          type: 'number',
        },
        {
          field: 'depositAmountCollected',
          label: 'Deposit Amount Collected',
          type: 'number',
        },
        {
          field: 'depositsReturned',
          label: 'Deposits Returned',
          type: 'number',
        },
        {
          field: 'depositAmountReturned',
          label: 'Deposit Amount Returned',
          type: 'number',
        },
      ],
    };
  },
  created() {
    requests.getUserLeaderboard().then((response) => {
      this.leaderboard = response.data;
      this.loading = false;
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card>
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <AdvancedTable
                :loading="loading"
                :columns="columns"
                :data="leaderboard"
                title="Leaderboard">
            </AdvancedTable>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
