<template>
  <div>
    <span
      v-if="!this.$store.themeSettingsStore.isOpenSettings"
      @click="this.$store.themeSettingsStore.isOpenSettings = !this.$store.themeSettingsStore.isOpenSettings"
      class="fixed ltr:md:right-[-32px] ltr:right-0 rtl:left-0 rtl:md:left-[-32px] top-1/2 z-[888] translate-y-1/2 bg-slate-800 text-slate-50 dark:bg-slate-700 dark:text-slate-300 cursor-pointer transform rotate-90 flex items-center text-sm font-medium px-2 py-2 shadow-deep ltr:rounded-b rtl:rounded-t"
    >
      <Icon
        icon="heroicons:cog-6-tooth"
        class="text-slate-50 text-lg animate-spin"
      />
      <span class="hidden md:inline-block ltr:ml-2 rtl:mr-2"
        >Settings</span
      ></span
    >
    <Transition name="lefttranslate">
      <div
        v-show="this.$store.themeSettingsStore.isOpenSettings"
        class="setting-wrapper fixed ltr:right-0 rtl:left-0 top-0 md:w-[400px] w-[300px] bg-white dark:bg-slate-800 h-screen z-[9999] px-6 md:pb-6 pb-[100px] shadow-base2 dark:shadow-base3 border border-gray-5002 dark:border-slate-700"
        data-simplebar
      >
        <header
          class="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 -mx-6 px-6 py-[15px] mb-6"
        >
          <div>
            <span
              class="block text-xl text-slate-900 font-medium dark:text-[#eee]"
              >Theme customizer</span
            >
            <span
              class="block text-sm font-light text-[#68768A] dark:text-[#eee]"
              >Customize & Preview in Real Time</span
            >
          </div>
          <div
            class="cursor-pointer text-2xl text-slate-800 dark:text-slate-200"
            @click="this.$store.themeSettingsStore.isOpenSettings = false"
          >
            <Icon icon="heroicons-outline:x" />
          </div>
        </header>
        <div class="space-y-4">
          <Skin />
          <Theme />
          <hr class="-mx-6 border-slate-200 dark:border-slate-700" />
          <Semidark />
          <Monochrome />
          <div><Rlt /></div>
          <hr class="-mx-6 border-slate-200 dark:border-slate-700" />
          <Width />
          <div class="xl:block hidden">
            <MenuLayout />
          </div>
          <hr class="-mx-6 border-slate-200 dark:border-slate-700" />

          <Navbar />
          <Footer v-if="window.width > 768" />
        </div>
      </div>
    </Transition>
    <Transition name="overlay-fade">
      <div
        v-if="this.$store.themeSettingsStore.isOpenSettings"
        class="overlay bg-white bg-opacity-0 fixed inset-0 z-[999]"
        @click="this.$store.themeSettingsStore.isOpenSettings = false"
      ></div>
    </Transition>
  </div>
</template>
<script>
import Icon from "../Icon";
import Footer from "./Tools/Footer";
import MenuLayout from "./Tools/MenuLayout";
import Navbar from "./Tools/Navbar";
import Skin from "./Tools/Skin";
import Width from "./Tools/Width";
import window from "@/mixins/window";
import Theme from "./Tools/Theme";
import Semidark from "./Tools/Semidark";
import Monochrome from "./Tools/Monochrome";
import Rlt from "./Tools/Rtl.vue";
export default {
  mixins: [window],
  components: {
    Icon,
    Width,
    Skin,
    MenuLayout,
    Navbar,
    Theme,
    Footer,
    Semidark,
    Monochrome,
    Rlt,
  },
  data() {
    return {};
  },
};
</script>
<style lang="css" scoped>
@keyframes lefttranslate {
  0% {
    opacity: 0;
    transform: translateX(20px);
  }
  100% {
    opacity: 1;
    transform: translateX(0px);
  }
}

@keyframes overlay-fade {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

.overlay-fade-enter-active {
  animation: overlay-fade 0.3s;
}
.overlay-fade-leave-active {
  animation: overlay-fade 0.3s reverse;
}

.lefttranslate-enter-active {
  animation: lefttranslate 0.24s;
}

.lefttranslate-leave-active {
  animation: lefttranslate 0.24s reverse;
}
</style>
