<script>
import AdvancedTable from '@/components/Tables/AdvancedTable.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';

export default {
  name: 'clientLeaderboard',
  components: {Card, AdvancedTable},
  data() {
    return {
      loading: true,
      leaderboard: [],
      columns: [
        {
          field: 'fullName',
          label: 'Full Name',
        },
        {
          field: 'contracts',
          label: 'Contracts',
          type: 'number',
        },
        {
          field: 'appointments',
          label: 'Appointments',
          type: 'number',
        },
        {
          field: 'appointmentsConfirmed',
          label: 'Confirmed Appointments',
          type: 'number',
        },
        {
          field: 'appointmentsCancelled',
          label: 'Cancelled Appointments',
          type: 'number',
        },
        {
          field: 'appointmentsDenied',
          label: 'Denied Appointments',
          type: 'number',
        },
        {
          field: 'appointmentsPending',
          label: 'Pending Appointments',
          type: 'number',
        },
      ],
    };
  },
  created() {
    requests.getClientLeaderboard().then((response) => {
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