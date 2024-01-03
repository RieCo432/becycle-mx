<template>
  <Dropdown
    classMenuItems="md:w-[335px] w-min top-[58px]"
    classItem="px-4 py-2"
  >
    <span
      class="relative lg:h-[32px] lg:w-[32px] lg:bg-gray-500-f7 bg-slate-50 lg:dark:bg-slate-900 dark:text-white text-slate-900 cursor-pointer rounded-full text-[20px] flex flex-col items-center justify-center"
      ><Icon icon="heroicons-outline:mail" />
      <span
        class="absolute lg:right-0 lg:top-0 -top-2 -right-2 h-4 w-4 bg-red-500 text-[8px] font-semibold flex flex-col items-center justify-center rounded-full text-white z-[99]"
        >10</span
      >
    </span>
    <template v-slot:menus>
      <div
        class="flex justify-between px-4 py-4 border-b border-slate-100 dark:border-slate-600"
      >
        <div
          class="text-sm text-slate-800 dark:text-white font-medium leading-6"
        >
          Messages
        </div>
        <div class="text-slate-800 dark:text-white text-xs md:text-right">
          <router-link :to="{ name: 'chat' }" class="underline"
            >View all</router-link
          >
        </div>
      </div>
      <div class="divide-y divide-slate-100 dark:divide-slate-800">
        <MenuItem
          v-slot="{ active }"
          v-for="(item, i) in message.slice(0, 3)"
          :key="i"
        >
          <div
            :class="`${
              active
                ? 'bg-slate-100 text-slate-800 dark:bg-slate-600 dark:bg-opacity-70'
                : 'text-slate-600 dark:text-slate-300'
            } block w-full px-4 py-2 text-sm  cursor-pointer`"
          >
            <div
              class="flex ltr:text-left rtl:text-right space-x-3 rtl:space-x-reverse"
            >
              <div class="flex-none">
                <div
                  class="h-8 w-8 bg-white dark:bg-slate-700 rounded-full relative"
                >
                  <span
                    :class="`${
                      item.active ? 'bg-secondary-500' : 'bg-green-500'
                    } w-[10px] h-[10px] rounded-full border border-white dark:border-slate-700  inline-block absolute right-0 top-0`"
                  ></span>
                  <img
                    :src="item.image"
                    alt=""
                    class="block w-full h-full object-cover rounded-full border hover:border-white border-transparent"
                  />
                </div>
              </div>
              <div class="flex-1">
                <div
                  class="text-slate-800 dark:text-slate-300 text-sm font-medium mb-1`"
                >
                  {{ item.title }}
                </div>
                <div
                  class="text-xs hover:text-[#68768A] text-slate-600 dark:text-slate-300 mb-1"
                >
                  {{ item.desc }}
                </div>
                <div class="text-slate-400 dark:text-slate-400 text-xs">
                  3 min ago
                </div>
              </div>
              <div class="flex-0" v-if="item.hasnotifaction">
                <span
                  class="h-4 w-4 bg-danger-500 border border-white rounded-full text-[10px] flex items-center justify-center text-white"
                >
                  {{ item.notification_count }}
                </span>
              </div>
            </div>
          </div>
        </MenuItem>
      </div>
    </template>
  </Dropdown>
</template>
<script>
import Dropdown from "@/components/Dropdown";
import Icon from "@/components/Icon";
import { MenuItem } from "@headlessui/vue";
import { message } from "../../../constant/data";
export default {
  components: {
    Icon,
    Dropdown,
    MenuItem,
  },
  data() {
    return {
      message,
    };
  },
};
</script>
<style lang=""></style>
