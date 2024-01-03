<template>
  <div class="md:mb-6 mb-4 flex space-x-3 rtl:space-x-reverse">
    <h4
      v-if="this.$route.name && !this.$route.meta.groupParent"
      :class="
        this.$route.meta.groupParent
          ? 'lg:border-r lg:border-secondary-500'
          : ''
      "
      class="font-medium lg:text-2xl text-xl capitalize text-slate-900 inline-block ltr:pr-4 rtl:pl-4"
    >
      {{ this.$route.name.replace("-", " ") }}
    </h4>
    <ul class="breadcrumbs" v-if="this.$route.meta.groupParent">
      <li class="text-primary-500">
        <router-link :to="{ name: 'home' }" class="text-lg">
          <Icon icon="heroicons-outline:home" />
        </router-link>
        <span class="breadcrumbs-icon rtl:transform rtl:rotate-180">
          <Icon icon="heroicons:chevron-right" />
        </span>
      </li>
      <li class="text-primary-500">
        <button type="button" class="capitalize">
          {{ this.$route.meta.groupParent }}
        </button>
        <span class="breadcrumbs-icon rtl:transform rtl:rotate-180">
          <Icon icon="heroicons:chevron-right" />
        </span>
      </li>
      <li class="capitalize text-slate-500 dark:text-slate-400">
        {{ this.$route.name.replace("-", " ") }}
      </li>
    </ul>
  </div>
</template>
<script>
import Icon from "@/components/Icon";
export default {
  components: {
    Icon,
  },
};
</script>
<style lang="scss">
.breadcrumbs {
  @apply flex text-sm space-x-2 items-center;
  li {
    @apply relative flex items-center space-x-2 capitalize font-normal rtl:space-x-reverse;
    .breadcrumbs-icon {
      @apply text-lg text-secondary-500 dark:text-slate-500;
    }
  }
}
</style>
