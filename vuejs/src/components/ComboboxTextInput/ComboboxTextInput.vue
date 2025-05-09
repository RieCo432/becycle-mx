<template>
  <Combobox
      @update:modelValue="(value) => selected($event, value)">
    <div class="relative mt-0">
      <div
          class="relative w-full"
      >



        <div
            class="fromGroup relative"
            :class="`${error ? 'has-error' : ''}  ${horizontal ? 'flex' : ''}  ${
      validate ? 'is-valid' : ''
    } `"
        >
          <label
              v-if="label"
              :class="`${classLabel} ${
        horizontal ? 'flex-0 mr-6 md:w-[100px] w-[60px] break-words' : ''
      }  ltr:inline-block rtl:block input-label `"
              :for="name"
          >
            {{ label }}</label
          >
          <div class="relative" :class="horizontal ? 'flex-1' : ''">

            <ComboboxInput
                as="template"
            >
              <input
                  :type="types"
                  :name="name"
                  :placeholder="placeholder"
                  :class="`${classInput} input-control w-full block focus:outline-none h-[40px] ${
          hasicon ? 'ltr:pr-10 rtl:pl-10' : ''
        } `"
                  :value="modelValue"
                  @input="$emit('update:modelValue', $event.target.value)"
                  :error="error"
                  :id="name"
                  :readonly="isReadonly"
                  :disabled="disabled"
                  :validate="validate"
                  v-if="!isMask"
              />
            </ComboboxInput>
            <cleave
                :class="`${classInput} cleave input-control block w-full focus:outline-none h-[40px] `"
                :name="name"
                :placeholder="placeholder"
                :value="modelValue"
                @input="$emit('update:modelValue', $event.target.value)"
                :error="error"
                :id="name"
                :readonly="isReadonly"
                :disabled="disabled"
                :validate="validate"
                :options="options"
                v-if="isMask"
                modelValue="modelValue"
            />

            <div
                class="flex text-xl absolute ltr:right-[14px] rtl:left-[14px] top-1/2 -translate-y-1/2"
            >
        <span
            v-if="hasicon"
            @click="toggleType"
            class="cursor-pointer text-secondary-500"
        >
          <Icon icon="heroicons-outline:eye" v-if="types === 'password'" />
          <Icon icon="heroicons-outline:eye-off" v-else />
        </span>

              <span v-if="error" class="text-danger-500">
          <Icon icon="heroicons-outline:information-circle" />
        </span>

              <span v-if="validate" class="text-success-500">
          <Icon icon="bi:check-lg" />
        </span>
            </div>
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

      </div>
        <ComboboxOptions
            class="absolute w-full mt-1 max-h-60 overflow-auto rounded-md py-1 text-base ring-1 ring-black/5
                 focus:outline-none sm:text-sm bg-white dark:bg-slate-800 dark:border dark:border-slate-700
                 shadow-dropdown z-[9999]"
            :static="openByDefault"
        >
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
import Icon from '@/components/Icon';
import Cleave from 'vue-cleave-component';
export default {
  components: {
    Combobox,
    ComboboxOptions,
    ComboboxOption,
    ComboboxInput,
    Icon,
    Cleave,
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
    openByDefault: {
      type: Boolean,
      default: false,
    },
    placeholder: {
      type: String,
      default: 'Search',
    },
    label: {
      type: String,
    },
    classLabel: {
      type: String,
      default: ' ',
    },
    classInput: {
      type: String,
      default: 'classinput',
    },
    type: {
      type: String,
      default: 'text',
      // required: true,
    },
    name: {
      type: String,
    },
    modelValue: {
      type: String,
      default: '',
    },
    error: {
      type: String,
    },
    hasicon: {
      type: Boolean,
      default: false,
    },
    isReadonly: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
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
    isMask: {
      type: Boolean,
      default: false,
    },
    options: {
      type: Object,
      default: () => ({
        creditCard: true,
        delimiter: '-',
      }),
    },
  },
  data() {
    return {
      types: this.type,
    };
  },
  methods: {
    selected(event, value) {
      const i = this.suggestions.indexOf(value);
      this.selectedCallback(event, i);
    },
    toggleType() {
      // toggle the type of the input field
      this.types = this.types === 'text' ? 'password' : 'text';
    },
  },
};
</script>

<style scoped lang="scss">

</style>
