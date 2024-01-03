<template>
  <footer :class="footerClass()">
    <div
      class="site-footer px-6 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-300 py-4"
    >
      <div class="grid md:grid-cols-2 grid-cols-1 md:gap-5">
        <div class="text-center ltr:md:text-start rtl:md:text-right text-sm">
          COPYRIGHT &copy; 2022 DashCode, All rights Reserved
        </div>
        <div class="ltr:md:text-right rtl:md:text-end text-center text-sm">
          Hand-crafted & Made by
          <a
            href="https://codeshaper.net"
            target="_blank"
            class="text-primary-500 font-semibold"
          >
            Codeshaper
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>
<script>
export default {
  methods: {
    footerClass() {
      switch (this.$store.themeSettingsStore.footerType) {
        case "sticky":
          return "sticky bottom-0 z-[999]";
        case "static":
          return "static";
        case "hidden":
          return "hidden";
      }
    },
  },
};
</script>
<style lang=""></style>
