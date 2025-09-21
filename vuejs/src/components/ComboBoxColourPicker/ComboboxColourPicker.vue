<template>
  <div
      @mouseleave="(evt) => {
           showSuggestions = false;
         }"
      @mouseenter="() => (showSuggestions = true)">
    <div class="relative mt-0">
      <div class="relative w-full">
        <div
            class="fromGroup relative"
            :class="`${error ? 'has-error' : ''}  ${horizontal ? 'flex' : ''}  ${validate ? 'is-valid' : ''} `">
          <label
              v-if="label"
              :class="`${classLabel} ${
                horizontal
                ? 'flex-0 mr-6 md:w-[100px] w-[60px] break-words'
                : ''}
                ltr:inline-block rtl:block input-label `"
              :for="name">
            {{ label }}
          </label>
          <div v-if="allColours" class="relative" :class="horizontal ? 'flex-1' : ''">
            <div class="grid grid-cols-8 gap-2">
              <div v-for="colour in allColours" :key="colour.id" class="flex items-center justify-center">
                <Tooltip placement="top" arrow theme="dark">
                  <template #button>
                    <div>
                      <Icon
                          v-if="internalModelValue.map((c) => (c.hex)).includes(colour.hex)"
                          icon="heroicons-outline:check"
                          class="text-white px-0 py-0 absolute bg-blue-500 rounded-full" />
                      <div
                          :class="[
                              'w-10', 'h-10', 'rounded-full', 'border-2',
                              internalModelValue.map((c) => (c.hex)).includes(colour.hex)
                              ? 'border-blue-500'
                              : ' border-transparent']"
                          :style="{backgroundColor: colour.hex}"
                          @click="colourClick(colour)"
                      />
                    </div>
                  </template>
                  <span>{{ colour.name }} ({{ colour.hex }})</span>
                </Tooltip>
              </div>
            </div>
            <div class="flex text-xl absolute ltr:right-[14px] rtl:left-[14px] top-1/2 -translate-y-1/2">
              <span
                  v-if="hasicon"
                  @click="toggleType"
                  class="cursor-pointer text-secondary-500">
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
              :class="msgTooltip
              ? ' inline-block bg-danger-500 text-white text-[10px] px-2 py-1 rounded'
              : ' text-danger-500 block text-sm'">{{ error }}
          </span>
          <span
              v-if="validate"
              class="mt-2"
              :class="
              msgTooltip
              ? ' inline-block bg-success-500 text-white text-[10px] px-2 py-1 rounded'
              : ' text-success-500 block text-sm'">
            {{ validate }}
          </span>
          <span
              class="block text-secondary-500 font-light leading-4 text-xs mt-2"
              v-if="description">
            {{ description }}
          </span>
        </div>
      </div>
        <div
            class="absolute w-full max-h-60 overflow-auto rounded-md py-1 text-base ring-1 ring-black/5
                 focus:outline-none sm:text-sm bg-white dark:bg-slate-800 dark:border dark:border-slate-700
                 shadow-dropdown z-[9999]"
            v-if="openByDefault || showSuggestions"
            @mouseenter="() => (showSuggestions = true)"
        >
          <ul>
            <li
                v-if="((suggestions.indexOf(fieldModelValue) === -1) && allowNew)"
                :class="{
                      'bg-slate-100 text-slate-900 dark:bg-slate-600 dark:text-slate-300 dark:bg-opacity-50': activeIndex === -1,
                      'text-slate-600 dark:text-slate-300': activeIndex !== -1,
                      }"
                class="relative w-full cursor-default select-none py-2 px-4"
                @mouseenter="() => (activeIndex = -1)">
              <span class="block">
                Create {{ fieldModelValue }}
              </span>
            </li>
            <li
                v-for="(suggestion, i) in suggestions"
                :key="i"
                :class="{
                      'bg-slate-100 text-slate-900 dark:bg-slate-600 dark:text-slate-300 dark:bg-opacity-50': activeIndex === i,
                      'text-slate-600 dark:text-slate-300': !activeIndex !== i,
                      }"
                class="relative cursor-default select-none py-2 px-4"
                @mouseenter="() => (activeIndex = i)"
                @mousedown.prevent="(event) => selected(event, suggestion)">
              <slot name="suggestion" :suggestion="suggestion" :index="i" :active="activeIndex === i">
                <span class="block">
                  {{ prettyPrintFunction(suggestion) }}
                </span>
              </slot>
            </li>
          </ul>
        </div>
      </div>
  </div>
</template>


<script>
import Icon from '@/components/Icon';
import {delay} from 'lodash-es';
import requests from '@/requests';
import Tooltip from '@/components/Tooltip/index.vue';
export default {
  components: {
    Tooltip,
    Icon,
  },
  emits: ['emptied'],
  props: {
    suggestions: {
      type: Array,
      default: () => [],
    },
    selectedCallback: {
      type: Function,
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
    prettyPrintFunction: {
      type: Function,
      default: (value) => value,
    },
  },
  data() {
    return {
      types: this.type,
      showSuggestions: false,
      activeIndex: -1,
      allColours: null,
      internalModelValue: [],
    };
  },
  methods: {
    delay,
    selected(event, value) {
      this.showSuggestions = false;
      const i = this.suggestions.indexOf(value);
      this.selectedCallback(event, i);
    },
    toggleType() {
      // toggle the type of the input field
      this.types = this.types === 'text' ? 'password' : 'text';
    },
    fetchColours() {
      requests.getColours().then((response) => {
        this.allColours = response.data;
      });
    },
    colourClick(colour) {
      const hexMap = this.internalModelValue.map((c) => c.hex);
      if (hexMap.includes(colour.hex)) {
        const indexInArray = hexMap.findIndex((hexCode) => colour.hex === hexCode);
        this.internalModelValue.splice(indexInArray, 1);
      } else {
        this.internalModelValue.push(colour);
      }
      this.$emit('update:modelValue', this.internalModelValue);
      if (this.internalModelValue.length === 0) {
        this.$emit('emptied');
      };
    },
  },
  created() {
    this.fetchColours();
  },
  watch: {
    modelValue: {
      immediate: true,
      handler(value) {
        this.internalModelValue = value ? value : [];
      },
    },
  },
};
</script>

<style scoped lang="scss">

</style>
