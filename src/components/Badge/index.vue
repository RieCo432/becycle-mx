<template>
  <span class="badge" :class="badgeClass">
    <span v-if="!$slots.default" class="inline-flex items-center">
      <span v-if="icon" class="inline-block ltr:mr-1 rtl:ml-1"
        ><Icon :icon="icon" /> </span
      >{{ label }}</span
    >
    <span v-if="$slots.default" class="inline-flex items-center"
      ><slot></slot
    ></span>
  </span>
</template>
<script>
import Icon from "@/components/Icon";
export default {
  components: {
    Icon,
  },
  props: {
    label: {
      type: String,
      default: "primary-500",
    },
    badgeClass: {
      type: String,
      default: "bg-primary-500 text-white",
    },
    icon: {
      type: String,
      default: "",
    },
  },
};
</script>
<style lang="scss" scoped>
.badge {
  @apply py-1 px-2 text-xs  capitalize font-semibold rounded-[.358rem] whitespace-nowrap  align-baseline inline-flex;
  &.pill {
    @apply rounded-[999px];
  }
}
</style>
