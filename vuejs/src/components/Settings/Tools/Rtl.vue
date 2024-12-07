<template>
  <div>
    <div class="flex justify-between mt-6 items-center">
      <div class="text-slate-600 text-base dark:text-slate-300">RTL</div>
      <div>
        <label
          :class="direction ? 'bg-primary-500' : 'bg-secondary-500'"
          class="relative inline-flex h-6 w-[46px] items-center rounded-full transition-all duration-150 cursor-pointer"
        >
          <input type="checkbox" v-model="direction" class="hidden" />
          <span
            :class="
              direction
                ? 'ltr:translate-x-6 rtl:-translate-x-6'
                : 'ltr:translate-x-[2px] rtl:translate-x-[-2px]'
            "
            class="inline-block h-5 w-5 transform rounded-full bg-white transition-all duration-150"
          />
        </label>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      direction: this.$store.themeSettingsStore.direction,
    };
  },
  mounted() {
  },
  watch: {
    direction: {
      handler() {
        if (this.direction) {
          this.$store.themeSettingsStore.direction = this.direction;
          document.documentElement.setAttribute("dir", "rtl");
          localStorage.setItem("direction", this.direction);
        } else {
          this.$store.themeSettingsStore.direction = this.direction;
          document.documentElement.setAttribute("dir", "ltr");
          localStorage.setItem("direction", this.direction);
        }
      },
      immediate: true,
    },
  },
};
</script>
<style lang=""></style>
