<template>
  <router-link :to="{ name: 'home' }">
    <img
      :src="`/logo/${resourcesSubdir}/default.svg`"
      alt=""
      v-if="!this.$store.themeSettingsStore.isDark"
    />

    <img
      :src="`/logo/${resourcesSubdir}/white.svg`"
      alt=""
      v-if="this.$store.themeSettingsStore.isDark"
    />
  </router-link>
</template>
<script>
const RESOURCES_SUB_DIR = import.meta.env.VITE_RESOURCES_SUB_DIR;


export default {
  data() {
    return {
      resourcesSubdir: RESOURCES_SUB_DIR,
    };
  },
};
</script>
