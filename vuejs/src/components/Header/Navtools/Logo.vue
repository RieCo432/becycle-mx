<template>
  <router-link :to="{ name: 'home' }">
    <img
      :src="`/src/assets/images/logo/${RESOURCES_SUB_DIR}/default.svg`"
      alt=""
      v-if="!this.$store.themeSettingsStore.isDark"
    />

    <img
      :src="`/src/assets/images/logo/${RESOURCES_SUB_DIR}/white.svg`"
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
      RESOURCES_SUB_DIR: RESOURCES_SUB_DIR,
    };
  },
};
</script>
