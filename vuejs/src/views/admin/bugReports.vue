<script>
import Card from "@/components/Card/index.vue";
import requests from "@/requests";
import AdvancedTable from "@/components/Tables/AdvancedTable.vue";
import Modal from "@/components/Modal/Modal.vue";
import {useToast} from "vue-toastification";
import DashButton from "@/components/Button/index.vue";

const toast = useToast();

export default {
  name: "bugReports",
  components: {DashButton, Modal, AdvancedTable, Card},
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
        {
          label: 'Delete Bug Report',
          icon: 'heroicons-outline:trash',
          func: (bugReportId) => this.deleteBugReport(bugReportId),
        },
      ],
      selectedRows: [],
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
    formatDescription(description) {
      if (description.length > 50)
        return description.substring(0, 50) + '...';
      return description
    },
    viewBugReport(bugReportId) {
      const bugReport = this.bugReports.find(bugReport => bugReport.id === bugReportId)
      this.$store.bugReportingStore.openModal(bugReport);
    },
    deleteBugReport(bugReportId) {
      const shouldDelete = confirm('Are you sure to delete this bug report?')
      if (!shouldDelete)
        return;

      requests.deleteBugReport(bugReportId).then(() => {
        const index = this.bugReports.findIndex(bugReport => bugReport.id === bugReportId)
        this.bugReports.splice(index, 1);
        toast.success('Bug report deleted', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    selectedRowsChanged(selectedRows) {
      this.selectedRows = selectedRows
    },
    mergeBugReports() {
      const shouldMerge = confirm('Are you sure to merge these bug reports?')
      if (!shouldMerge)
        return;

      const bugReportIds = this.selectedRows.map((bugReport) => bugReport.id);

      requests.mergeBugReports(bugReportIds).then((response) => {
        const mergedIndex = this.bugReports.findIndex(bugReport => bugReport.id === response.data.id)
        this.bugReports.splice(mergedIndex, 1, response.data);

        for (let id of bugReportIds) {
          if (id === response.data.id)
            continue;
          const index = this.bugReports.findIndex(bugReport => bugReport.id === id)
          this.bugReports.splice(index, 1);
        }
        toast.success('Bug reports merged', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
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
                ref="bugReportsTable"
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
                @selected-rows-change="selectedRowsChanged"
            >
              <template v-slot:selectedRowActions>
                <DashButton text="Merge Selected Bug Reports"
                            :isDisabled="selectedRows.length < 2"
                            @click="mergeBugReports"></DashButton>
              </template>
            </AdvancedTable>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">
:deep(.vgt-selection-info-row) {
  display: flex;
  align-items: center;
  height: 60px;
}

:deep(.vgt-pull-right) {
  margin-left: auto;
}

:deep(.vgt-table td) {
  text-transform: none;
}
</style>