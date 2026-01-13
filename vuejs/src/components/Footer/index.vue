<template>
  <footer :class="footerClass()">
    <div
      class="site-footer px-6 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-300 py-4"
    >
      <div class="grid md:grid-cols-3 grid-cols-2 md:gap-5">
        <div class="text-center ltr:md:text-start rtl:md:text-right text-sm col-span-2">
          COPYRIGHT &copy; 2023-2026 Colin Ries, on behalf of {{ OFFICIAL_NAME }}, All rights Reserved. {{ REGISTRATION_NUMBER }}
        </div>
        <div class="ltr:md:text-right rtl:md:text-end text-center text-sm">
          Made by Colin Ries
        </div>
      </div>
    </div>
  </footer>
</template>
<script>
const OFFICIAL_NAME = import.meta.env.VITE_OFFICIAL_NAME;
const REGISTRATION_NUMBER = import.meta.env.VITE_REGISTRATION_NUMBER;
export default {
  data() {
    return {
      OFFICIAL_NAME: OFFICIAL_NAME,
      REGISTRATION_NUMBER: REGISTRATION_NUMBER,
    };
  },
  methods: {
    footerClass() {
      switch (this.$store.themeSettingsStore.footerType) {
      case 'sticky':
        return 'sticky bottom-0 z-[999]';
      case 'static':
        return 'static';
      case 'hidden':
        return 'hidden';
      }
    },
  },
};
</script>
<style lang=""></style>
