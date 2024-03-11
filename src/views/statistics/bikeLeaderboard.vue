<script>
import AdvancedTable from '@/components/Tables/AdvancedTable.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import VueSelect from '@/components/Select/VueSelect.vue';
import {sum} from 'lodash-es';

export default {
  name: 'bikeLeaderboard',
  components: {VueSelect, Card, AdvancedTable},
  data() {
    return {
      loading: true,
      groupByOptions: [
        'none',
        'make',
        'model',
      ],
      selectedGroupBy: null,
      rawLeaderboard: [],
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
        {
          field: 'actions',
          label: 'Actions',
        },
      ],
      actions: [
        {
          label: 'View Bike',
          icon: 'heroicons-outline:eye',
          func: (bikeId) => this.$router.push({path: `/bikes/${bikeId}`}),
        },
      ],
    };
  },
  created() {
    this.selectedGroupBy = this.groupByOptions[0];
    this.fetchBikeLeaderboard();
  },
  methods: {
    fetchBikeLeaderboard() {
      this.loading = true;
      requests.getBikeLeaderboard(this.selectedGroupBy).then((response) => {
        this.rawLeaderboard = response.data;
        this.loading = false;
      });
    },
  },
  computed: {
    leaderboard() {
      if (this.selectedGroupBy === 'none') {
        return this.rawLeaderboard;
      } else {
        const makes = [...new Set(this.rawLeaderboard.map((bike) => bike.make))];
        return makes.map((make) => {
          const bikesOfMake = this.rawLeaderboard.filter((bike) => bike.make === make);
          const models = [...new Set(bikesOfMake.map((bike) => bike.model))];
          if (this.selectedGroupBy === 'make') {
            const colours = [...new Set(bikesOfMake.map((bike) => bike.colour))];
            return {
              make: `${make} (${bikesOfMake.length})`,
              model: `${models.length} models`,
              colour: `${colours.length} colours`,
              decals: undefined,
              serialNumber: undefined,
              contracts: sum(bikesOfMake.map((bike) => bike.contracts)),
            };
          } else if (this.selectedGroupBy === 'model') {
            return models.map((model) => {
              const bikesOfModel = this.rawLeaderboard.filter((bike) => bike.make === make && bike.model === model);
              const colours = [...new Set(bikesOfModel.map((bike) => bike.colour))];
              return {
                make: make,
                model: `${model} (${bikesOfModel.length})`,
                colour: `${colours.length} colours`,
                decals: undefined,
                serialNumber: undefined,
                contracts: sum(bikesOfModel.map((bike) => bike.contracts)),
              };
            });
          } else {
            return [];
          }
        }).flat();
      }
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card>
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-12">
            <VueSelect
                label="Group By"
                :options="groupByOptions"
                v-model="selectedGroupBy"
            ></VueSelect>
          </div>
          <div class="col-span-12">
            <AdvancedTable
                :loading="loading"
                :columns="columns"
                :data="leaderboard"
                title="Leaderboard"
                :actions="actions"
            >
            </AdvancedTable>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
