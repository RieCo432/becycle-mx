<script>
import Card from '@/components/Card/index.vue';
import {ref} from 'vue';
import AppointmentTypesTable from '@/components/Tables/AppointmentTypesTable.vue';
import requests from '@/requests';

export default {
  name: 'appointmentTypes',
  components: {AppointmentTypesTable, Card},
  setup() {
    const appointmentTypes = ref([]);

    return {
      appointmentTypes,
    }
  },
  methods: {
    openEditAppointmentTypeModal(appointmentTypeId) {

    },
    patchAppointmentType(appointmentTypeId, patchData) {

    }
  },
  data() {
    return {
      loadingAppointmentTypes: true,
      appointmentTypesActions: [
        {
          label: 'Edit',
          icon: 'heroicons-outline:pencil-square',
          func: this.openEditAppointmentTypeModal,
        },
      ],
      appointmentTypesColumns: [
        {
          label: 'ID',
          field: 'id',
        },
        {
          label: 'Active',
          field: 'active',
        },
        {
          label: 'Title',
          field: 'title',
        },
        {
          label: 'Description',
          field: 'description',
        },
        {
          label: 'Duration (minutes)',
          field: 'duration',
        },
        {
          label: 'Actions',
          field: 'actions',
        },
      ],
    };
  },
  created() {
    requests.getAppointmentTypes(true).then((response) => {
      this.appointmentTypes = response.data;
      this.loadingAppointmentTypes = false;
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="2xl:col-span-9 col-span-12">
      <Card title="Appointment Types">
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <AppointmentTypesTable :loading="loadingAppointmentTypes" :actions="appointmentTypesActions" :columns="appointmentTypesColumns" :table-data="appointmentTypes"></AppointmentTypesTable>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>