<template>
  <router-link :to="{ name: 'home' }">
    <img
      src="@/assets/images/logo/logo.svg"
      alt=""
      v-if="!this.$store.themeSettingsStore.isDark"
    />

    <img
      src="@/assets/images/logo/logo-white.svg"
      alt=""
      v-if="this.$store.themeSettingsStore.isDark"
    />
  </router-link>
</template>
<script></script>
