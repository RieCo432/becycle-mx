<template>
  <Combobox>
    <div class="relative mt-0">
      <div
          class="relative w-full"
      >
        <ComboboxInput as="template">
          <slot></slot>
        </ComboboxInput>
      </div>
      <ComboboxOptions
          class="absolute w-full mt-1 max-h-60 overflow-auto rounded-md py-1 text-base ring-1 ring-black/5 focus:outline-none sm:text-sm bg-white dark:bg-slate-800 dark:border dark:border-slate-700 shadow-dropdown z-[9999]">
        <ComboboxOption
            v-if="((suggestions.indexOf(fieldModelValue) === -1) && allowNew)"
            :value="fieldModelValue"
            v-slot="{ active }"
            as="template"
        >
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
            as="template"
            @mousedown="(event) => selectedCallback(event, i)"
        >
          <li
              :class="{
                      'bg-slate-100 text-slate-900 dark:bg-slate-600 dark:text-slate-300 dark:bg-opacity-50': active,
                      'text-slate-600 dark:text-slate-300': !active,
                      }"
              class="relative cursor-default select-none py-2 px-4"
          >
                      <span class="block">
                        {{ suggestion }}
                      </span>
          </li>
        </ComboboxOption>
      </ComboboxOptions>
    </div>
  </Combobox>
</template>


<script>
import {Combobox, ComboboxInput, ComboboxOptions, ComboboxOption} from '@headlessui/vue';
import {bool} from "yup";

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
    allowNew: {
      type: Boolean,
      default: true,
    },
  },
};
</script>

<style scoped lang="scss">

</style>
