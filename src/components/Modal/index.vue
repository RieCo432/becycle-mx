<template>
  <TransitionRoot :show="activeModal" as="template">
    <Dialog as="div" class="relative z-[99999]">
      <TransitionChild
        :enter="noFade ? '' : 'duration-300 ease-out'"
        :enter-from="noFade ? '' : 'opacity-0'"
        :enter-to="noFade ? '' : 'opacity-100'"
        :leave="noFade ? '' : 'duration-200 ease-in'"
        :leave-from="noFade ? '' : 'opacity-100'"
        :leave-to="noFade ? '' : 'opacity-0'"
      >
        <div
          class="fixed inset-0 bg-slate-900/50 backdrop-filter backdrop-blur-sm"
          v-if="disableBackdrop === false"
        />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div
          class="flex min-h-full justify-center text-center p-6"
          :class="centered ? 'items-center' : 'items-start '"
        >
          <TransitionChild
            as="template"
            :enter="noFade ? '' : 'duration-300  ease-out'"
            :enter-from="noFade ? '' : 'opacity-0 scale-95'"
            :enter-to="noFade ? '' : 'opacity-100 scale-100'"
            :leave="noFade ? '' : 'duration-200 ease-in'"
            :leave-from="noFade ? '' : 'opacity-100 scale-100'"
            :leave-to="noFade ? '' : 'opacity-0 scale-95'"
          >
            <DialogPanel
              class="w-full transform overflow-hidden rounded-md bg-white dark:bg-slate-800 text-left align-middle shadow-xl transition-all"
              :class="sizeClass"
            >
              <div
                class="relative overflow-hidden py-4 px-5 text-white flex justify-between"
                :class="themeClass"
              >
                <h2
                  v-if="title"
                  class="capitalize leading-6 tracking-wider font-medium text-base text-white"
                >
                  {{ title }}
                </h2>
                <button @click="close" class="text-[22px]">
                  <Icon icon="heroicons-outline:x" />
                </button>
              </div>
              <div
                class="px-6 py-8"
                :class="scrollContent ? 'overflow-y-auto max-h-[400px]' : ''"
              >
                <slot />
              </div>
              <div
                class="px-4 py-3 flex justify-end space-x-3 border-t border-slate-100 dark:border-slate-700"
                v-if="$slots.footer"
              >
                <slot name="footer"></slot>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script>
import Icon from '@/components/Icon';

import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
} from '@headlessui/vue';

export default {
  components: {
    Icon,
    TransitionRoot,
    TransitionChild,
    Dialog,
    DialogPanel,
  },

  props: {
    centered: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      default: 'Basic Modal',
    },
    label: {
      type: String,
      default: 'Basic Modal',
    },
    disableBackdrop: {
      type: Boolean,
      default: false,
    },
    noFade: {
      type: Boolean,
      default: false,
    },
    themeClass: {
      type: String,
      default:
        'bg-slate-900 dark:bg-slate-800 dark:border-b dark:border-slate-700',
    },
    sizeClass: {
      type: String,
      default: 'max-w-xl',
    },
    scrollContent: {
      type: Boolean,
      default: false,
    },
    activeModal: {
      type: Boolean,
      default: false,
    },
  },

  setup(props, { emit }) {
    const close = () => {
      emit('close');
    };
    return {
      close,
    };
  },
};
</script>
