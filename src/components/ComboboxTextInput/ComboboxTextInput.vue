<template>
  <Combobox>
    <ComboboxInput as="template">
      <slot></slot>
    </ComboboxInput>
    <!-- TODO: move the options menu so it sits below the input field -->
    <ComboboxOptions
      class="absolute w-max mt-1 max-h-60 overflow-auto rounded-md py-1 text-base ring-1 ring-black/5 focus:outline-none sm:text-sm bg-white dark:bg-slate-800 dark:border dark:border-slate-700 shadow-dropdown z-[9999]">
      <ComboboxOption
        v-if="suggestions.indexOf(fieldModelValue) === -1"
        :value="fieldModelValue"
        v-slot="{ active }">
        <li
          :class="{
                      'bg-slate-100 text-slate-900 dark:bg-slate-600 dark:text-slate-300 dark:bg-opacity-50': active,
                      'text-slate-600 dark:text-slate-300': !active,
                      }"
          class="relative w-full cursor-default select-none py-2 px-4"
        >
                      <span class="block">
                        Create {{ fieldModelValue }}
                      </span>
        </li>
      </ComboboxOption>
      <ComboboxOption
        v-for="(suggestion, i) in suggestions"
        :key="i"
        :value="suggestion"
        v-slot="{ active }"
        @click="selectedCallback"
      >
        <li
          :class="{
                      'bg-slate-100 text-slate-900 dark:bg-slate-600 dark:text-slate-300 dark:bg-opacity-50': active,
                      'text-slate-600 dark:text-slate-300': !active,
                      }"
          class="relative cursor-default select-none py-2 px-4"
        >
                      <span class="block truncate">
                        {{ suggestion }}
                      </span>
        </li>
      </ComboboxOption>
    </ComboboxOptions>
  </Combobox>
</template>


<script>
import {Combobox, ComboboxInput, ComboboxOptions, ComboboxOption} from '@headlessui/vue';

export default {
  components: {
    Combobox,
    ComboboxOptions,
    ComboboxOption,
    ComboboxInput,
  },
  props: {
    suggestions: {
      type: Array,
      default: () => [],
    },
    selectedCallback: {
      type: Function,
    },
    fieldModelValue: {
      type: String,
    },
  },
};
</script>

<style scoped lang="scss">

</style>
