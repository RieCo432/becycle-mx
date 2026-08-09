<script>
export default {
  name: 'NoInputCheckbox',
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    label: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    activeClass: {
      type: String,
      default:
        ' ring-black-500  bg-slate-900 dark:bg-slate-700 dark:ring-slate-700 ring-offset-2 dark:ring-offset-slate-800 ',
    },
    inactiveClass: {
      type: String,
      default:
        ' bg-slate-100 dark:bg-slate-600 dark:border-slate-600 ',
    },
    textClass: {
      type: String,
      default: ' text-slate-500 dark:text-slate-400 text-sm leading-6 ',
    },
    borderClass: {
      type: String,
      default: ' border-slate-100 dark:border-slate-800 ',
    },
  },
};
</script>

<template>
  <div>
    <label
      class="flex items-center"
      :class="disabled ? ' cursor-not-allowed opacity-50' : 'cursor-pointer'"
    >
      <span
        class="h-4 w-4 border flex-none rounded inline-flex
               ltr:mr-3 rtl:ml-3 relative transition-all duration-150"
        :class="
        borderClass +
          (value || value === null
            ? activeClass + ' ring-2  '
            : inactiveClass)
        "
      >
        <img
          src="@/assets/images/icon/ck-white.svg"
          alt=""
          class="h-[10px] w-[10px] block m-auto"
          v-if="value"
        />
      </span>
      <span
        :class="textClass"
        v-if="label"
      >
        {{ label }}
      </span>
    </label>
  </div>
</template>

<style scoped lang="scss">

</style>
