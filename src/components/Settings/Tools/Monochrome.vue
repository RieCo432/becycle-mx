<template>
    <div>
      <div class="flex justify-between mt-6 items-center">
        <div class="text-slate-600 text-base dark:text-slate-300">Monochrome Mode</div>
        <div>
          <label
            :class="monochrome==true ? 'bg-primary-500' : 'bg-secondary-500'"
            class="relative inline-flex h-6 w-[46px] items-center rounded-full transition-all duration-150 cursor-pointer"
          >
            <input type="checkbox" @change="toggleMonochrome" v-model="monochrome" class="hidden" />
            <span
              :class="
                monochrome
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
              monochrome: this.$store.themeSettingsStore.monochrome,
          };
      },
      mounted() {
      },
  
      methods: {
        toggleMonochrome() {
          this.$store.themeSettingsStore.toggleMonochrome();
        },
      },
  };
  </script>
  <style lang=""></style>
  