<template>
  <div
    :class="`mobile-sidebar bg-white dark:bg-slate-800  ${
      this.$store.themeSettingsStore.theme === 'bordered'
        ? 'border border-gray-5002'
        : 'shadow-base'
    }   `"
  >
    <div class="logo-segment flex justify-between items-center px-4 py-6">
      <router-link :to="{ name: 'home' }">
        <img
            :src="`/src/assets/images/logo/${RESOURCES_SUB_DIR}/full.svg`"
          alt=""
          v-if="!this.$store.themeSettingsStore.isDark"
        />

        <img
            :src="`/src/assets/images/logo/${RESOURCES_SUB_DIR}/full-white.svg`"
          alt=""
          v-if="this.$store.themeSettingsStore.isDark"
        />
      </router-link>
      <span
        class="cursor-pointer text-slate-900 dark:text-white text-2xl"
        @click="toggleMsidebar"
        ><Icon icon="heroicons:x-mark"
      /></span>
    </div>
    <simplebar class="mobile-menu px-4 h-[calc(100%-180px)]">
      <Navmenu :items="topMenu" />
    </simplebar>
    <div class="absolute bottom-0">
      <img :src="`/src/assets/images/registration/${RESOURCES_SUB_DIR}/blue/small-blue-landscape.png`" alt="Charity Registration Logo"/>
    </div>
  </div>
</template>
<script>
import Icon from '../Icon';
import {defineComponent} from 'vue';
import {topMenu} from '@/constant/data';
import Navmenu from './Navmenu';
import simplebar from 'simplebar-vue';
import 'simplebar/dist/simplebar.min.css';
import {useThemeSettingsStore} from '@/store/themeSettings';

const themeSettingsStore = useThemeSettingsStore();
const RESOURCES_SUB_DIR = import.meta.env.VITE_RESOURCES_SUB_DIR;

export default defineComponent({
  components: {
    Icon,
    Navmenu,
    simplebar,
  },
  data() {
    return {
      RESOURCES_SUB_DIR: RESOURCES_SUB_DIR,
      topMenu,
      openClass: 'w-[248px]',
      closeClass: 'w-[72px] close_sidebar',
    };
  },
  methods: {
    toggleMsidebar() {
      themeSettingsStore.toggleMsidebar();
    },
  },
});
</script>
<style lang="scss">
.mobile-sidebar {
  @apply fixed ltr:left-0 rtl:right-0 top-0   h-full   z-[9999]  w-[280px];
}
</style>
