<script>
import Card from "@/components/Card/index.vue";
import requests from "@/requests";
import AdvancedTable from "@/components/Tables/AdvancedTable.vue";
import Modal from "@/components/Modal/Modal.vue";

export default {
  name: "bugReports",
  components: {Modal, AdvancedTable, Card},
  data() {
    return {
      loading: true,
      bugReports: [],
      columns: [
        {
          field: 'reportedByUserName',
          label: 'Reported By User',
        },
        {
          field: 'reportedAt',
          label: 'Reported At',
          type: 'date',
          dateInputFormat: 'yyyy-MM-dd\'T\'HH:mm:ss.SSSSSS',
          dateOutputFormat: 'yyyy MMM do HH:mm:ss',
        },
        {
          field: 'pageAddress',
          label: 'Page Address',
          type: 'string',
        },
        {
          field: 'description',
          label: 'Description',
          type: 'string',
          formatFn: this.formatDescription
        },
        {
          field: 'actions',
          label: 'Actions',
        },
      ],
      actions: [
        {
          label: 'View Bug Report',
          icon: 'heroicons-outline:eye',
          func: (bugReportId) => this.viewBugReport(bugReportId),
        },
      ]
    };
  },
  created() {
    requests.getBugReports().then((response) => {
      this.bugReports = response.data;
      this.loading = false;
    });
  },
  computed: {
    shouldUpdateBugReport() {
      return this.$store.bugReportingStore.shouldUpdateBugReport
    }
  },
  methods: {
    viewBugReport(bugReportId) {
      const bugReport = this.bugReports.find(bugReport => bugReport.id === bugReportId)
      this.$store.bugReportingStore.openModal(bugReport);
    },
    formatDescription(description) {
      if (description.length > 50)
        return description.substring(0, 50) + '...';
      return description
    }
  },
  watch: {
    shouldUpdateBugReport(newValue) {
      if (newValue === true) {
        const index = this.bugReports.findIndex(bugReport => bugReport.id === this.$store.bugReportingStore.bugReport.id)
        if (index === -1)
          this.bugReports.push(this.$store.bugReportingStore.bugReport);
        else
          this.bugReports.splice(index, 1, this.$store.bugReportingStore.bugReport);
        this.$store.bugReportingStore.shouldUpdateBugReport = false
      }
    }
  }
}
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
                :data="bugReports"
                title="Bug Reports"
                :lineNumbers="false"
                :actions="actions"
                :selectOptions="{
                  enabled: true,
                  selectOnCheckboxOnly: true
                }"
            >
              <template v-slot:selectedRowActions>
              </template>
            </AdvancedTable>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">
:deep(.vgt-table td) {
  text-transform: none;
}
</style>