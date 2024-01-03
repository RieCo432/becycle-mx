<template>
  <div class="flex items-center space-x-3 rtl:space-x-reverse">
    <h4
      v-if="this.$route.name && !this.$route.meta.groupParent"
      :class="
        this.$route.meta.groupParent
          ? 'lg:border-r lg:border-secondary-500'
          : ''
      "
      class="font-medium lg:text-2xl text-xl capitalize text-slate-900 inline-block pr-4"
    >
      {{ this.$route.meta.groupParent }}
    </h4>
    <ul class="breadcrumbs" v-if="this.$route.meta.groupParent">
      <li class="text-primary-500">
        <router-link :to="{ nam: 'home' }" class="text-lg">
          <Icon icon="heroicons-outline:home" />
        </router-link>
        <span class="breadcrumbs-icon rtl:transform rtl:rotate-180">
          <Icon icon="heroicons:chevron-right" />
        </span>
      </li>
      <li class="text-primary-500">
        <button type="button" class="capitalize">
          {{ this.$route.name }}
        </button>
        <span class="breadcrumbs-icon rtl:transform rtl:rotate-180">
          <Icon icon="heroicons:chevron-right" />
        </span>
      </li>
      <li class="capitalize text-slate-500 dark:text-slate-400">
        {{ this.$route.meta.groupParent }}
      </li>
    </ul>
  </div>
</template>
<script setup>
import Icon from "@/components/Icon";
</script>
<style lang=""></style>
