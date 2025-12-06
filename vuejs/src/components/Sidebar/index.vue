<template>
  <div :class="this.$store.themeSettingsStore.semidark ? 'dark' : ''">
    <div
      :class="`sidebar-wrapper bg-white dark:bg-slate-800    ${
        this.$store.themeSettingsStore.skin === 'bordered'
          ? 'border-r border-gray-5002 dark:border-slate-700'
          : 'shadow-base'
      }   ${
        this.$store.themeSettingsStore.sidebarCollasp
          ? this.closeClass
          : this.openClass
      }
      ${this.$store.themeSettingsStore.isMouseHovered ? 'sidebar-hovered' : ''}

      `"
      @mouseenter="this.$store.themeSettingsStore.isMouseHovered = true"
      @mouseleave="this.$store.themeSettingsStore.isMouseHovered = false"
    >
      <div
        :class="` logo-segment flex justify-between items-center bg-white dark:bg-slate-800 z-[9] py-6  sticky top-0   px-4  ${
          this.$store.themeSettingsStore.sidebarCollasp
            ? this.closeClass
            : this.openClass
        } ${
          this.$store.themeSettingsStore.skin === 'bordered'
            ? ' border-b border-r border-gray-5002 dark:border-slate-700'
            : ' border-none'
        }
        ${this.$store.themeSettingsStore.isMouseHovered ? 'logo-hovered' : ''}

        `"
      >
        <router-link
          :to="{ name: 'home' }"
          v-if="
            !this.$store.themeSettingsStore.sidebarCollasp ||
            this.$store.themeSettingsStore.isMouseHovered
          "
        >
          <img
              :src="fullLogo"
            alt=""
            v-if="
              !this.$store.themeSettingsStore.isDark &&
              !this.$store.themeSettingsStore.semidark
            "
          />

          <img
            :src="fullWhiteLogo"
            alt=""
            v-if="
              this.$store.themeSettingsStore.isDark ||
              this.$store.themeSettingsStore.semidark
            "
          />
        </router-link>
        <router-link
          :to="{ name: 'home' }"
          v-if="
            this.$store.themeSettingsStore.sidebarCollasp &&
            !this.$store.themeSettingsStore.isMouseHovered
          "
        >
          <img
              :src="defaultLogo"
              alt=""
              v-if="
              !this.$store.themeSettingsStore.isDark &&
              !this.$store.themeSettingsStore.semidark
            "
          />
          <img
              :src="defaultWhiteLogo"
            alt=""
            v-if="
              this.$store.themeSettingsStore.isDark ||
              this.$store.themeSettingsStore.semidark
            "
          />
        </router-link>
        <div
            v-if="!this.$store.themeSettingsStore.sidebarCollasp"
            @click="
            this.$store.themeSettingsStore.sidebarCollasp =
              !this.$store.themeSettingsStore.sidebarCollasp
          "
            class="ml-auto h-full text-slate-900 dark:text-white text-xl flex items-center"
        >
          <Icon
              icon="heroicons-outline:arrow-left"
              v-if="!this.$store.themeSettingsStore.direction"
          />
          <Icon
              icon="heroicons-outline:arrow-right"
              v-if="this.$store.themeSettingsStore.direction"
          />
        </div>

      </div>
      <div
        class="h-[60px] absolute top-[80px] nav-shadow z-[1] w-full transition-all duration-200 pointer-events-none"
        :class="[shadowbase ? ' opacity-100' : ' opacity-0']"
      ></div>
      <simplebar :class="`sidebar-menu px-4 ${this.$store.themeSettingsStore.sidebarCollasp &&
        !this.$store.themeSettingsStore.isMouseHovered
            ? this.closeHeightClass
            : this.openHeightClass}`">
        <Navmenu :items="topMenu" />
      </simplebar>
      <div ref="scioLogo" class="absolute bottom-0">
        <img :src="registrationBanner" alt="Charity Registration Logo"/>
      </div>
    </div>
  </div>
</template>
<script>
import Icon from '../Icon';
// import { Icon } from "@iconify/vue";
import {defineComponent} from 'vue';
import {topMenu} from '@/constant/data';
import Navmenu from './Navmenu';
import simplebar from 'simplebar-vue';
import 'simplebar/dist/simplebar.min.css';

const RESOURCES_SUB_DIR = import.meta.env.VITE_RESOURCES_SUB_DIR;

const fullLogo = new URL(`/src/assets/images/logo/${RESOURCES_SUB_DIR}/full.svg`, import.meta.url).href;
const fullWhiteLogo = new URL(`/src/assets/images/logo/${RESOURCES_SUB_DIR}/full-white.svg`, import.meta.url).href;
const defaultLogo = new URL(`/src/assets/images/logo/${RESOURCES_SUB_DIR}/default.svg`, import.meta.url).href;
const defaultWhiteLogo = new URL(`/src/assets/images/logo/${RESOURCES_SUB_DIR}/white.svg`, import.meta.url).href;
const registrationBanner = new URL(
  `/src/assets/images/registration/${RESOURCES_SUB_DIR}/blue/small-blue-landscape.png`, import.meta.url).href;

export default defineComponent({
  components: {
    Icon,
    Navmenu,
    simplebar,
  },
  data() {
    return {
      fullLogo: fullLogo,
      fullWhiteLogo: fullWhiteLogo,
      defaultLogo: defaultLogo,
      defaultWhiteLogo: defaultWhiteLogo,
      registrationBanner: registrationBanner,
      topMenu,
      openClass: 'w-[248px]',
      closeClass: 'w-[72px] close_sidebar',
      openHeightClass: 'h-[calc(100%-187px)]',
      closeHeightClass: 'h-[calc(100%-106px)]',
    };
  },
  computed: {
    topAndBottomLogosHeight() {
      return this.$store.themeSettingsStore.sidebarCollasp ? '167px' : '106px';
    },
  },
});
</script>
<style lang="scss">
.sidebar-wrapper {
  @apply fixed ltr:left-0 rtl:right-0 top-0   h-screen   z-[999];
  transition: width 0.2s cubic-bezier(0.39, 0.575, 0.565, 1);
  will-change: width;
}

.nav-shadow {
  background: linear-gradient(
    rgb(255, 255, 255) 5%,
    rgba(255, 255, 255, 75%) 45%,
    rgba(255, 255, 255, 20%) 80%,
    transparent
  );
}
.dark {
  .nav-shadow {
    background: linear-gradient(
      rgba(#1e293b, 100%) 5%,
      rgba(#1e293b, 75%) 45%,
      rgba(#1e293b, 20%) 80%,
      transparent
    );
  }
}
.sidebar-wrapper.sidebar-hovered {
  width: 248px !important;
}
.logo-segment.logo-hovered {
  width: 248px !important;
}
</style>
