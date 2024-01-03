<template>
  <div>
    <button
      @click="openModal"
      class="flex items-center xl:text-sm text-lg xl:text-slate-400 text-slate-800 dark:text-slate-300 px-1 space-x-3 rtl:space-x-reverse"
    >
      <Icon icon="heroicons-outline:search" /><span
        class="xl:inline-block hidden"
        >Search...</span
      >
    </button>
  </div>
  <TransitionRoot :show="isOpen" as="template">
    <Dialog
      as="div"
      @close="closeModal"
      class="fixed inset-0 z-[9999] overflow-y-auto p-4 md:pt-[25vh] pt-20"
    >
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div
          class="fixed inset-0 bg-slate-900/60 backdrop-filter backdrop-blur-sm backdrop-brightness-10"
        />
      </TransitionChild>

      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0 scale-95"
        enter-to="opacity-100 scale-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100 scale-100"
        leave-to="opacity-0 scale-95"
      >
        <DialogPanel>
          <Combobox v-model="selected">
            <div class="relative">
              <div
                class="relative mx-auto max-w-xl rounded-md bg-white dark:bg-slate-800 shadow-2xl ring-1 ring-gray-500-500 dark:ring-light divide-y divide-gray-500-300 dark:divide-light"
              >
                <div
                  className="flex bg-white dark:bg-slate-800  px-3 rounded-md py-3 items-center"
                >
                  <div
                    className="flex-0  text-slate-700 dark:text-slate-300 ltr:pr-2 rtl:pl-2 text-lg"
                  >
                    <Icon icon="heroicons-outline:search" />
                  </div>
                  <ComboboxInput
                    class="bg-transparent outline-none focus:outline-none border-none w-full flex-1 dark:placeholder:text-slate-300 dark:text-slate-200"
                    placeholder="Search..."
                    @change="query = $event.target.value"
                  />
                </div>
                <TransitionRoot
                  leave="transition ease-in duration-100"
                  leaveFrom="opacity-100"
                  leaveTo="opacity-0"
                  @after-leave="query = ''"
                >
                  <ComboboxOptions
                    class="max-h-40 overflow-y-auto text-sm py-2"
                  >
                    <div v-if="filteredsearchList.length === 0 && query !== ''">
                      <div className=" text-base py-2 px-4">
                        <p
                          className="text-slate-500-600 text-base dark:text-white"
                        >
                          No result found
                        </p>
                      </div>
                    </div>

                    <ComboboxOption
                      v-for="item in filteredsearchList"
                      as="template"
                      :key="item.id"
                      :value="item"
                      v-slot="{ active }"
                    >
                      <li
                        class="px-4 text-[15px] font-normal capitalize py-2"
                        :class="{
                          'bg-primary-500 dark:bg-slate-600 dark:bg-opacity-60 text-white':
                            active,
                          'text-slate-900 dark:text-white': !active,
                        }"
                      >
                        <span>
                          {{ item.name }}
                        </span>
                      </li>
                    </ComboboxOption>
                  </ComboboxOptions>
                </TransitionRoot>
              </div>
            </div>
          </Combobox>
        </DialogPanel>
      </TransitionChild>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, computed } from "vue";
import Icon from "@/components/Icon";

import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
  Combobox,
  ComboboxInput,
  ComboboxOptions,
  ComboboxOption,
} from "@headlessui/vue";

const isOpen = ref(false);
const searchList = [
  {
    id: 1,
    name: "What is Dashcode ?",
  },
  {
    id: 2,
    name: "Our Services",
  },
  {
    id: 3,
    name: "Our Team",
  },
  {
    id: 4,
    name: "Our Clients",
  },
  {
    id: 5,
    name: "Our Partners",
  },
  {
    id: 6,
    name: "Our Blog",
  },
  {
    id: 7,
    name: "Our Contact",
  },
];

let selected = ref(searchList[0]);
let query = ref("");

let filteredsearchList = computed(() =>
  query.value === ""
    ? searchList
    : searchList.filter((item) =>
        item.name
          .toLowerCase()
          .replace(/\s+/g, "")
          .includes(query.value.toLowerCase().replace(/\s+/g, ""))
      )
);

function closeModal() {
  isOpen.value = false;
}
function openModal() {
  isOpen.value = true;
}
</script>
