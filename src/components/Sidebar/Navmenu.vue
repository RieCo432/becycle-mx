<template>
  <ul>
    <li
      v-for="(item, i) in items"
      :key="i"
      :class="`
      ${item.child ? 'item-has-children' : ''}
      ${activeSubmenu === i ? 'open' : ''}
      ${this.$route.name === item.link ? 'menu-item-active' : ''}
      
      `"
      class="single-sidebar-menu"
    >
      <!-- ?? single menu with no childred !!  -->

      <router-link
        :to="`${item.link}`"
        class="menu-link"
        v-if="!item.child && !item.isHeadr"
      >
        <span class="menu-icon" v-if="item.icon">
          <Icon :icon="item.icon"
        /></span>
        <div class="text-box" v-if="item.title">{{ item.title }}</div>
      </router-link>

      <!-- ?? only for menulabel ??  -->
      <div v-else-if="item.isHeadr && !item.child" class="menulabel">
        {{ item.title }}
      </div>
      <!-- !!sub menu parent li !! -->
      <div
        class="menu-link"
        v-else
        :class="
          activeSubmenu === i ? 'parent_active not-collapsed' : 'collapsed'
        "
        @click="toggleSubmenu(i)"
      >
        <div class="flex-1 flex items-start">
          <span class="menu-icon" v-show="item.icon">
            <Icon :icon="item.icon"
          /></span>
          <div class="text-box" v-if="item.title">{{ item.title }}</div>
        </div>
        <div class="flex-0">
          <div
            class="menu-arrow transform transition-all duration-300"
            :class="
              activeSubmenu === i
                ? ' ltr:rotate-90 rtl:rotate-90'
                : 'rtl:rotate-180'
            "
          >
            <Icon icon="heroicons-outline:chevron-right" />
          </div>
        </div>
      </div>
      <Transition
        enter-active-class="submenu_enter-active"
        leave-active-class="submenu_leave-active"
        @before-enter="beforeEnter"
        @enter="enter"
        @after-enter="afterEnter"
        @before-leave="beforeLeave"
        @leave="leave"
        @after-leave="afterLeave"
      >
        <!-- !! SubMenu !! -->
        <ul calss="sub-menu " v-if="i === activeSubmenu">
          <li
            v-for="(ci, index) in item.child"
            :key="index"
            class="block ltr:pl-4 rtl:pr-4 ltr:pr-1 rtl:-l-1 mb-4 first:mt-4"
          >
            <router-link :to="ci.childlink" v-slot="{ isActive }">
              <span
                class="text-sm flex space-x-3 rtl:space-x-reverse items-center transition-all duration-150"
                :class="
                  isActive
                    ? ' text-slate-900 dark:text-white font-medium'
                    : 'text-slate-600 dark:text-slate-300'
                "
              >
                <span
                  class="h-2 w-2 rounded-full border border-slate-600 dark:border-slate-300 inline-block flex-none"
                  :class="
                    isActive
                      ? ' bg-slate-900 dark:bg-slate-300 ring-4 ring-opacity-[15%] ring-black-500 dark:ring-slate-300 dark:ring-opacity-20'
                      : ''
                  "
                ></span>
                <span class="flex-1">
                  {{ ci.childtitle }}
                </span>
              </span>
            </router-link>
          </li>
        </ul>
      </Transition>
    </li>
    <li class="single-sidebar-menu">
      <a
        href="https://dashcode-doc.codeshaper.tech/"
        target="_blank"
        class="menu-link"
      >
        <span class="menu-icon"><Icon icon="heroicons:document" /></span>
        <div class="text-box">Documentation</div>
      </a>
    </li>
  </ul>
</template>
<script>
import { useRouter } from "vue-router";
import Icon from "../Icon";
export default {
  components: {
    Icon,
  },

  data() {
    return {
      activeSubmenu: null,
    };
  },

  props: {
    title: {
      type: String,
      default: "",
    },
    icon: {
      type: String,
      default: "",
    },
    link: {
      type: String,
      default: "",
    },
    items: { type: Array, required: true },
    childrenLinks: { type: Array, default: null },
  },

  methods: {
    beforeEnter(element) {
      requestAnimationFrame(() => {
        if (!element.style.height) {
          element.style.height = "0px";
        }

        element.style.display = null;
      });
    },
    enter(element) {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          element.style.height = `${element.scrollHeight}px`;
        });
      });
    },
    afterEnter(element) {
      element.style.height = null;
    },
    beforeLeave(element) {
      requestAnimationFrame(() => {
        if (!element.style.height) {
          element.style.height = `${element.offsetHeight}px`;
        }
      });
    },
    leave(element) {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          element.style.height = "0px";
        });
      });
    },
    afterLeave(element) {
      element.style.height = null;
    },
    toggleSubmenu(index) {
      if (this.activeSubmenu === index) {
        this.activeSubmenu = null;
      } else {
        this.activeSubmenu = index;
      }
    },
  },

  watch: {
    $route() {
      if (this.$store.themeSettingsStore.mobielSidebar) {
        this.$store.themeSettingsStore.mobielSidebar = false;
      }

      this.items.map((item) => {
        if (item.link === this.$route.name) {
          this.activeSubmenu = null;
        }
      });
    },
  },

  created() {
    const router = useRouter();
    this.items.map((item, i) => {
      item.child?.map((ci) => {
        if (ci.childlink === router.currentRoute.value.name) {
          this.activeSubmenu = i;
        }
      });
    });
  },
  // update if route chnage then activesubmenu null

  updated() {},
};
</script>
<style lang="scss">
.submenu_enter-active,
.submenu_leave-active {
  overflow: hidden;
  transition: all 0.34s linear;
}

.not-collapsed .has-icon {
  transition: all 0.34s linear;
}
.not-collapsed .has-icon {
  @apply transform rotate-180;
}

// single sidebar menu css
.single-sidebar-menu {
  @apply relative;
  .menulabel {
    @apply text-slate-800 dark:text-slate-300 text-xs font-semibold uppercase mb-4 mt-4;
  }
  > .menu-link {
    @apply flex text-slate-600 font-medium dark:text-slate-300 text-sm capitalize px-[10px] py-3 rounded-[4px] cursor-pointer;
  }
  .menu-icon {
    @apply icon-box inline-flex items-center text-slate-600 dark:text-slate-300 text-lg ltr:mr-3 rtl:ml-3;
  }
}
// menu item has chilren
.item-has-children {
  .menu-arrow {
    @apply h-5 w-5 text-base text-slate-300 bg-slate-100 dark:bg-[#334155] dark:text-slate-300 rounded-full flex justify-center items-center;
  }
}

// close sidebar css
.close_sidebar .menulabel {
  @apply hidden;
}

.close_sidebar:not(.sidebar-hovered) {
  .menu-arrow {
    @apply hidden;
  }
  .single-sidebar-menu {
    .text-box {
      @apply absolute  left-full ml-5 w-[180px] top-0 px-4 py-3 bg-white shadow-dropdown rounded-[4px] dark:bg-slate-800 z-[999] invisible opacity-0 transition-all duration-150;
    }
    &:hover {
      .text-box {
        @apply visible opacity-100;
      }
    }
  }
  .item-has-children {
    .text-box {
      @apply hidden;
    }

    > ul {
      @apply ml-4 absolute left-full top-0 w-[230px] bg-white shadow-dropdown rounded-[4px] dark:bg-slate-800 z-[999] px-4 pt-3 transition-all duration-150 invisible opacity-0;
      display: block !important;
    }
    &:hover {
      > ul {
        @apply visible opacity-100;
      }
    }
  }
}

// active menu
.item-has-children {
  .parent_active {
    @apply bg-secondary-500 bg-opacity-20;
    .icon-box,
    .menu-icon,
    .text-box {
      @apply text-slate-700 dark:text-slate-200;
    }
    .menu-arrow {
      @apply bg-secondary-500 text-slate-600 text-opacity-70 bg-opacity-30 dark:text-white;
    }
  }
}
.menu-item-active {
  .menu-link {
    @apply bg-slate-800 dark:bg-slate-700;
    .icon-box,
    .menu-icon,
    .text-box {
      @apply text-white dark:text-slate-300;
    }
  }
}
</style>
