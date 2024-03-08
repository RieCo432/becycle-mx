<script>
import AdvancedTable from '@/components/Tables/AdvancedTable.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';

export default {
  name: 'bikeLeaderboard',
  components: {Card, AdvancedTable},
  data() {
    return {
      loading: true,
      leaderboard: [],
      columns: [
        {
          field: 'make',
          label: 'Make',
        },
        {
          field: 'model',
          label: 'Model',
        },
        {
          field: 'colour',
          label: 'Colour',
        },
        {
          field: 'decals',
          label: 'Decals',
        },
        {
          field: 'serialNumber',
          label: 'Serial Number',
        },
        {
          field: 'contracts',
          label: 'Contracts',
          type: 'number',
        },
      ],
    };
  },
  created() {
    requests.getBikeLeaderboard().then((response) => {
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