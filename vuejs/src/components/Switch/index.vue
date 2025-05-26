<template>
  <div>
    <label
      class="flex items-start"
      :class="disabled ? ' cursor-not-allowed opacity-40' : 'cursor-pointer'"
    >
      <input
        type="checkbox"
        class="hidden"
        :disabled="disabled"
        :name="name"
        @change="onInput"
        :value="modelValue"
        v-bind="$attrs"
      />
      <div
        :class="modelValue ? activeClass : 'bg-secondary-500'"
        class="relative inline-flex h-6 w-[46px] ltr:mr-3 rtl:ml-3 items-center rounded-full transition-all duration-150"
      >
        <span
          v-if="badge && modelValue"
          :class="icon ? 'text-sm' : ' text-[9px]'"
          class="absolute left-1 top-1/2 -translate-y-1/2 capitalize font-bold text-white tracking-[1px]"
        >
          <span v-if="!icon">on</span>

          <Icon :icon="prevIcon" v-if="icon" />
        </span>
        <span
          v-if="badge && !ck"
          :class="icon ? 'text-sm' : ' text-[9px]'"
          class="absolute right-1 top-1/2 -translate-y-1/2 capitalize font-bold text-slate-900 tracking-[1px]"
        >
          <Transition>
            <span v-if="!icon">Off</span>
          </Transition>
          <Transition>
            <Icon :icon="nextIcon" v-if="icon" />
          </Transition>
        </span>

        <span
          :class="
            modelValue
              ? 'ltr:translate-x-6 rtl:-translate-x-6'
              : 'ltr:translate-x-[2px] rtl:-translate-x-[2px]'
          "
          class="inline-block h-5 w-5 transform rounded-full bg-white transition-all duration-150"
        />
      </div>

      <span
        class="text-slate-500 dark:text-slate-400 text-sm leading-6"
        v-if="label"
      >
        {{ label }}
      </span>
    </label>
  </div>
</template>
<script>
import Icon from '@/components/Icon';
import {defineComponent} from 'vue';
export default defineComponent({
  name: 'Switch',
  inheritAttrs: false,
  components: {
    Icon,
  },
  props: {
    label: {
      type: String,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    name: {
      type: String,
      default: 'checkbox',
    },
    activeClass: {
      type: String,
      default: 'bg-slate-900 dark:bg-slate-900 ',
    },
    modelValue: {
      type: null,
    },
    badge: {
      type: Boolean,
      default: false,
    },
    icon: {
      type: Boolean,
      default: false,
    },
    prevIcon: {
      type: String,
      default: 'heroicons-outline:volume-up',
    },
    nextIcon: {
      type: String,
      default: 'heroicons-outline:volume-off',
    },
  },
  emits: {
    'update:modelValue': (newValue) => ({
      modelValue: newValue,
    }),
    'update': (newValue) => ({
      newValue: newValue,
    }),
  },
  methods: {
    onInput() {
      this.$emit('update:modelValue', !this.modelValue);
      this.$emit('update', !this.modelValue);
    },
  },
});
</script>
<style lang=""></style>
