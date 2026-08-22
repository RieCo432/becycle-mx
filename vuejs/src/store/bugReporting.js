import {defineStore} from 'pinia';

export const useBugReportingStore = defineStore('bugReporting', {
    state: () => ({
        modalVisible: false,
        modalTitle: 'Report Bug',
        bugReport: {},
        shouldUpdateBugReport: false,
    }),
    actions: {
        openModal(bugReport) {
            this.modalVisible = true;
            this.modalTitle = bugReport.id == null ? 'Report Bug' : 'View Bug Report';
            this.bugReport = bugReport;
        },
        closeModal() {
            this.modalVisible = false;
        }
    },
});
