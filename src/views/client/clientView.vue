<script>
import Card from '@/components/Card/index.vue';
import Advanced from '@/components/Tables/ContractSummaryTable.vue';

export default {
  name: 'clientView',
  components: {
    Card,
    Advanced,
  },
  props: {
    client: {
      required: true,
      type: Object,
    },
    contractSummaries: {
      required: true,
      type: Array,
    },
  },

  data() {
    return {

      actions: [
        {
          name: 'View',
          icon: 'heroicons-outline:eye',
        },
        {
          name: 'Return',
          icon: 'heroicons:pencil-square',
        },
      ],
      options: [
        {
          value: '1',
          label: '1',
        },
        {
          value: '3',
          label: '3',
        },
        {
          value: '5',
          label: '5',
        },
      ],
      columns: [
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
          label: 'Make',
          field: 'bikeMake',
        },
        {
          label: 'Model',
          field: 'bikeModel',
        },

        {
          label: 'Colour',
          field: 'bikeColour',
        },

        {
          label: 'Decals',
          field: 'bikeDecals',
        },

        {
          label: 'Serial Number',
          field: 'bikeSerialNumber',
        },
        {
          label: 'Action',
          field: 'action',
        },
      ],


    };
  },
  computed: {
    name() {
      return this.client.firstName + ' ' + this.client.lastName;
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card :title="name">

        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <Advanced :options="options" :actions="actions" :columns="columns" :advanced-table="contractSummaries" title="Contracts"></Advanced>
          </div>
        </div>
      </Card>
    </div>
  </div>

</template>

<style scoped lang="scss">

</style>
