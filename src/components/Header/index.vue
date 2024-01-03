<template>
  <header :class="navbarTypeClass()">
    <div
      :class="`app-header md:px-6 px-[15px]  dark:bg-slate-800 shadow-base dark:shadow-base3 bg-white ${borderSwicthClass()} ${
        this.$store.themeSettingsStore.navbarColor
      }
      ${
        this.$store.themeSettingsStore.menuLayout === 'horizontal' && window.width > 1280
          ? 'py-1'
          : 'md:py-6 py-3'
      }
      `"
    >
      <div class="flex justify-between items-center h-full">
        <div
          v-if="this.$store.themeSettingsStore.menuLayout === 'vertical'"
          class="flex items-center md:space-x-4 space-x-2 rtl:space-x-reverse"
        >
          <button
            class="ltr:mr-5 rtl:ml-5 text-xl text-slate-900 dark:text-white"
            v-if="this.$store.themeSettingsStore.sidebarCollasp && window.width > 1280"
            @click="this.$store.themeSettingsStore.sidebarCollasp = false"
          >
            <Icon
              icon="akar-icons:arrow-right"
              v-if="!this.$store.themeSettingsStore.direction"
            />
            <Icon
              icon="akar-icons:arrow-left"
              v-if="this.$store.themeSettingsStore.direction"
            />
          </button>
          <MobileLogo v-if="window.width < 1280" />
          <handle-mobile-menu
            v-if="window.width < 1280 && window.width > 768"
          />
          <SearchModal />
        </div>
        <div
          v-if="this.$store.themeSettingsStore.menuLayout === 'horizontal'"
          class="flex items-center space-x-4 rtl:space-x-reverse"
        >
          <Logo v-if="window.width > 1280" />
          <MobileLogo v-else />
          <handle-mobile-menu v-if="window.width < 1280" />
        </div>
        <Mainnav
          v-if="
            this.$store.themeSettingsStore.menuLayout === 'horizontal' && window.width > 1280
          "
        />
        <div
          class="nav-tools flex items-center lg:space-x-6 space-x-3 rtl:space-x-reverse"
        >
          <LanguageVue />
          <SwitchDark />
          <MonochromeMode />
          <Message v-if="window.width > 768" />
          <Notification v-if="window.width > 768" />
          <Profile v-if="window.width > 768" />
          <handle-mobile-menu v-if="window.width < 768" />
        </div>
      </div>
    </div>
  </header>
</template>
<script>
import Profile from "./Navtools/Profile.vue";
import Notification from "./Navtools/Notification.vue";
import Message from "./Navtools/Message.vue";
import SwitchDark from "./Navtools/SwitchDark.vue";
import MonochromeMode from "./Navtools/MonochromeMode.vue";
import Mainnav from "./horizental-nav.vue";
import Icon from "../Icon";
import SearchModal from "./Navtools/SearchModal.vue";
import LanguageVue from "./Navtools/Language.vue";
import Logo from "./Navtools/Logo.vue";
import MobileLogo from "./Navtools/MobileLogo.vue";
import window from "@/mixins/window";
import HandleMobileMenu from "./Navtools/HandleMobileMenu.vue";

export default {
  mixins: [window],
  components: {
    Profile,
    Notification,
    Message,
    SwitchDark,
    MonochromeMode,
    Mainnav,
    Icon,
    LanguageVue,
    SearchModal,
    Logo,
    MobileLogo,
    HandleMobileMenu,
  },

  methods: {
    navbarTypeClass() {
      switch (this.$store.themeSettingsStore.navbarType) {
        case "floating":
          return "floating";
        case "sticky":
          return "sticky top-0 z-[999]";
        case "static":
          return "static";
        case "hidden":
          return "hidden";
        default:
          return "sticky top-0";
      }
    },
    borderSwicthClass() {
      if (
        this.$store.themeSettingsStore.skin === "bordered" &&
        this.$store.themeSettingsStore.navbarType !== "floating"
      ) {
        return "border-b border-gray-5002 dark:border-slate-700";
      } else if (
        this.$store.themeSettingsStore.skin === "bordered" &&
        this.$store.themeSettingsStore.navbarType === "floating"
      ) {
        return "border border-gray-5002 dark:border-slate-700";
      } else {
        return "dark:border-b dark:border-slate-700 dark:border-opacity-60";
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.floating .app-header {
  @apply md:mx-6 md:my-8 mx-[15px] my-[15px] rounded-md;
}
</style>
