<template>
  <router-view />
</template>

<script>
import { useThemeSettingsStore } from "@/store/themeSettings";

export default {
  mounted() {
    this.$store.themeSettingsStore = useThemeSettingsStore()
  }
}
</script>

<style></style>
