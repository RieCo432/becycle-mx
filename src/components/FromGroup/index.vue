<template>
  <div
    class="fromGroup relative"
    :class="`${error ? 'has-error' : ''}  ${horizontal ? 'flex' : ''}  ${
      validate ? 'is-valid' : ''
    } `"
  >
    <label
      v-if="label"
      :class="`${classLabel} inline-block input-label `"
      :for="name"
    >
      {{ label }}</label
    >
    <div class="relative">
      <slot></slot>
    </div>

    <span
      v-if="error"
      class="mt-2"
      :class="
        msgTooltip
          ? ' inline-block bg-danger-500 text-white text-[10px] px-2 py-1 rounded'
          : ' text-danger-500 block text-sm'
      "
      >{{ error }}</span
    >
    <span
      v-if="validate"
      class="mt-2"
      :class="
        msgTooltip
          ? ' inline-block bg-success-500 text-white text-[10px] px-2 py-1 rounded'
          : ' text-success-500 block text-sm'
      "
      >{{ validate }}</span
    >
    <span
      class="block text-secondary-500 font-light leading-4 text-xs mt-2"
      v-if="description"
      >{{ description }}</span
    >
  </div>
</template>
<script>
export default {
  components: {},
  props: {
    label: {
      type: String,
    },
    classLabel: {
      type: String,
      default: " ",
    },
    classInput: {
      type: String,
      default: "classinput",
    },

    name: {
      type: String,
    },

    error: {
      type: String,
    },

    horizontal: {
      type: Boolean,
      default: false,
    },
    validate: {
      type: String,
    },
    msgTooltip: {
      type: Boolean,
      default: false,
    },

    description: {
      type: String,
    },
  },
};
</script>
<style lang="scss"></style>
