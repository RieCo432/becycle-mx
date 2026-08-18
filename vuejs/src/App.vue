<template>
  <router-view/>
</template>

<script>
import {useThemeSettingsStore} from '@/store/themeSettings';
import {useBugReportingStore} from "@/store/bugReporting";

export default {
  mounted() {
    this.$store.themeSettingsStore = useThemeSettingsStore();
    this.$store.bugReportingStore = useBugReportingStore();
  }
};
</script>

<style></style>
