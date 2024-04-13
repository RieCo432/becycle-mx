<script>
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import requests from '@/requests';

export default {
  name: 'rawData',
  components: {DashButton, Card},
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
  },
};
</script>

<template>
  <div class="grid grid-cols-1">
    <div class="col-span-1">
      <Card title="Raw Data Access">
        <template #header>
          <DashButton @click="downloadRawDataExcel">Download Excel</DashButton>
        </template>
        Test
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>