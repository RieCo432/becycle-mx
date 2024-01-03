<template>
  <div>
    <div class="col-span-12 text-slate-600 dark:text-slate-300 text-base mb-2">
      Content Width
    </div>
    <div class="grid md:grid-cols-3 grid-cols-1 gap-3">
      <div v-for="(item, i) in contentWidths" :key="i">
        <label
          :for="`contentWidth_id${i}`"
          class="flex items-center text-sm text-slate-500 dark:text-slate-400 cursor-pointer"
        >
          <input
            class="hidden"
            type="radio"
            name="contentWidth"
            :id="`contentWidth_id${i}`"
            :value="item.value"
            v-model="contentWidth"
          />
          <span
            :class="item.value === contentWidth ? 'shadow-inset-4' : ''"
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
      contentWidth: this.$store.themeSettingsStore.cWidth,

      contentWidths: [
        {
          value: "full",
          label: "Full Width",
        },
        {
          value: "boxed",
          label: "Boxed",
        },
      ],
    };
  },
  mounted() {
  },

  watch: {
    contentWidth: {
      handler() {
        switch (this.contentWidth) {
          case "full":
            this.$store.themeSettingsStore.cWidth = this.contentWidth;

            break;
          case "boxed":
            this.$store.themeSettingsStore.cWidth = this.contentWidth;

            break;

          default:
            this.$store.themeSettingsStore.cWidth = this.contentWidth;
        }
      },
      immediate: true,
    },
  },
};
</script>
<style lang=""></style>
