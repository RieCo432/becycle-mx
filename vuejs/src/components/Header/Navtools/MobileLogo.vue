<template>
  <router-link :to="{ name: 'home' }">
    <img
        :src="defaultLogo"
        alt=""
        v-if="!this.$store.themeSettingsStore.isDark"
    />

    <img
        :src="defaultWhiteLogo"
        alt=""
        v-if="this.$store.themeSettingsStore.isDark"
    />
  </router-link>
</template>
<script>
const RESOURCES_SUB_DIR = import.meta.env.VITE_RESOURCES_SUB_DIR;
const defaultLogo = new URL(`/src/assets/images/logo/${RESOURCES_SUB_DIR}/default.svg`, import.meta.url).href;
const defaultWhiteLogo = new URL(`/src/assets/images/logo/${RESOURCES_SUB_DIR}/white.svg`, import.meta.url).href;

export default {
  data() {
    return {
      defaultLogo: defaultLogo,
      defaultWhiteLogo: defaultWhiteLogo,
    };
  },
};
</script>
