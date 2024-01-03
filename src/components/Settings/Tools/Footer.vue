<template>
  <div>
    <div
      class="col-span-12 text-slate-600 dark:text-slate-300 text-base mb-3 mt-6"
    >
      Footer Type
    </div>
    <div class="grid md:grid-cols-4 grid-cols-1 gap-3">
      <div v-for="(item, i) in footerTypes" :key="i">
        <label
          :for="`foo_type${i}`"
          class="text-slate-500 dark:text-slate-400 text-sm cursor-pointer flex items-center"
        >
          <input
            class="hidden"
            type="radio"
            name="footerType"
            :id="`foo_type${i}`"
            :value="item.value"
            v-model="footer"
          />
          <span
            :class="item.value === footer ? 'shadow-inset-4' : ''"
            class="flex-none h-4 w-4 bg-white dark:bg-transparent rounded-full border border-secondary-500 inline-block ltr:mr-3 rtl:ml-3 transition-all duration-150"
          ></span>
          {{ item.label }}
        </label>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      footer: this.$store.themeSettingsStore.footerType,
      footerTypes: [
        {
          value: "sticky",
          label: "Sticky",
        },
        {
          value: "static",
          label: "Static",
        },
        {
          value: "hidden",
          label: "Hidden",
        },
      ],
    };
  },
  mounted() {

  },
  watch: {
    footer: {
      handler() {
        switch (this.footer) {
          case "floating":
            this.$store.themeSettingsStore.footerType = this.footer;

            break;
          case "sticky":
            this.$store.themeSettingsStore.footerType = this.footer;

            break;
          case "static":
            this.$store.themeSettingsStore.footerType = this.footer;

            break;
          case "hidden":
            this.$store.themeSettingsStore.footerType = this.footer;

            break;
          default:
            this.$store.themeSettingsStore.footerType = this.footer;
        }
      },
      immediate: true,
    },
  },
};
</script>
<style lang=""></style>
