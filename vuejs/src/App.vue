<template>
  <router-view/>
</template>

<script>
import {useThemeSettingsStore} from '@/store/themeSettings';
import {useBugReportingStore} from "@/store/bugReporting";
import {usePermissionStore} from "@/store/permissionStore";

export default {
  mounted() {
    this.$store.themeSettingsStore = useThemeSettingsStore();
    this.$store.bugReportingStore = useBugReportingStore();
    this.$store.permissionStore = usePermissionStore();
  }
};
</script>

<style></style>
