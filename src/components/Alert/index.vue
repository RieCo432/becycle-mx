<template>
  <div
    v-if="!isDestroy"
    class="py-[18px] px-6 font-normal text-sm rounded-md"
    :class="alertClass() + ' ' + className"
  >
    <div class="flex items-start space-x-3 rtl:space-x-reverse">
      <div class="flex-0 text-[22px]" v-if="icon">
        <Icon :icon="icon" />
      </div>
      <div class="flex-1">
        <slot></slot>
      </div>
      <div
        class="flex-0 text-2xl cursor-pointer"
        @click="destroy"
        v-if="dismissible"
      >
        <Icon icon="heroicons-outline:x" />
      </div>
    </div>
  </div>
</template>
<script>
import Icon from "@/components/Icon";
export default {
  components: {
    Icon,
  },
  name: "Alert",
  type: "primary-500",

  props: {
    type: {
      type: String,
    },
    dismissible: {
      type: Boolean,
      default: false,
    },
    icon: {
      type: String,
    },
    className: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      isDestroy: false,
    };
  },
  methods: {
    destroy() {
      this.isDestroy = true;
    },

    alertClass() {
      switch (this.type) {
        case "primary-light":
          return "bg-primary-500 bg-opacity-[14%] text-primary-500";
        case "secondary-light":
          return "bg-secondary-500 bg-opacity-[14%] text-slate-600";
        case "success-light":
          return "bg-success-500 bg-opacity-[14%] text-success-500";
        case "info-light":
          return "bg-info-500 bg-opacity-[14%] text-info-500";
        case "warning-light":
          return "bg-warning-500 bg-opacity-[14%] text-warning-500";
        case "danger-light":
          return "bg-danger-500 bg-opacity-[14%] text-danger-500";
        case "dark-light":
          return "bg-slate-800 bg-opacity-[14%] text-slate-800 dark:bg-slate-500 dark:bg-opacity-[14%]  dark:text-slate-300";
        case "primary":
          return "bg-primary-500 text-white";
        case "secondary":
          return "bg-secondary-500 text-white";
        case "success":
          return "bg-success-500 text-white";
        case "info":
          return "bg-info-500 text-white";
        case "warning":
          return "bg-warning-500 text-white";
        case "danger":
          return "bg-danger-500 text-white";
        case "dark":
          return "bg-slate-800 text-white dark:bg-slate-900 dark:text-slate-300";
        case "primary-outline":
          return "bg-white text-primary-500 border border-primary-500 dark:bg-slate-800";
        case "secondary-outline":
          return "bg-white text-secondary-500 border border-secondary-500 dark:bg-slate-800";
        case "success-outline":
          return "bg-white text-success-500 border border-success-500 dark:bg-slate-800";
        case "info-outline":
          return "bg-white text-info-500 border border-info-500 dark:bg-slate-800";
        case "warning-outline":
          return "bg-white text-warning-500 border border-warning-500 dark:bg-slate-800";
        case "danger-outline":
          return "bg-white text-danger-500 border border-danger-500 dark:bg-slate-800";
        case "dark-outline":
          return "bg-white text-slate-800 dark:text-slate-300 border border-slate-800 dark:border-slate-600  dark:bg-slate-800";

        default:
          return "bg-white text-slate-900 dark:bg-slate-900 dark:text-slate-300";
      }
    },
  },
};
</script>
<style lang=""></style>
