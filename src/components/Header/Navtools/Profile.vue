<template>
  <Dropdown classMenuItems=" w-[180px] top-[58px] ">
    <div class="flex items-center">
      <div
        class="flex-none text-slate-600 dark:text-white text-sm font-normal items-center lg:flex hidden overflow-hidden text-ellipsis whitespace-nowrap"
      >
        <span
          class="overflow-hidden text-ellipsis whitespace-nowrap w-[85px] block"
          >{{ name }}</span
        >
        <span class="text-base inline-block ltr:ml-[10px] rtl:mr-[10px]"
          ><Icon icon="heroicons-outline:chevron-down"></Icon
        ></span>
      </div>
    </div>
    <template #menus>
      <MenuItem v-slot="{ active }" v-for="(item, i) in ProfileMenu" :key="i">
        <div
          type="button"
          :class="`${
            active
              ? 'bg-slate-100 dark:bg-slate-700 dark:bg-opacity-70 text-slate-900 dark:text-slate-300'
              : 'text-slate-600 dark:text-slate-300'
          } `"
          class="inline-flex items-center space-x-2 rtl:space-x-reverse w-full px-4 py-2 first:rounded-t last:rounded-b font-normal cursor-pointer"
          @click="item.link()"
        >
          <div class="flex-none text-lg">
            <Icon :icon="item.icon" />
          </div>
          <div class="flex-1 text-sm">
            {{ item.label }}
          </div>
        </div>
      </MenuItem>

      <MenuItem v-slot="{ active }">
        <div
          type="button"
          :class="`${
            active
              ? 'bg-slate-100 dark:bg-slate-700 dark:bg-opacity-70 text-slate-900 dark:text-slate-300'
              : 'text-slate-600 dark:text-slate-300'
          } `"
          class="inline-flex items-center space-x-2 rtl:space-x-reverse w-full px-4 py-2 first:rounded-t last:rounded-b font-normal cursor-pointer"
          @click="logout"
        >
          <div class="flex-none text-lg">
            <Icon icon="heroicons-outline:logout" />
          </div>
          <div class="flex-1 text-sm">
            Logout
          </div>
        </div>
      </MenuItem>
    </template>
  </Dropdown>
</template>
<script>
import {MenuItem} from '@headlessui/vue';
import Dropdown from '@/components/Dropdown';
import Icon from '@/components/Icon';
import {ProfileMenu} from '@/constant/data';
import {useCredentialsStore} from '@/store/credentialsStore';

const credentialsStore = useCredentialsStore();


export default {
  props: ['name'],
  components: {
    Icon,
    Dropdown,
    MenuItem,
  },
  data() {
    return {
      ProfileMenu: ProfileMenu.map( (item) => ({
        label: item.label,
        icon: item.icon,
        link: () => {
          this.$router.push(item.link);
        }})),
    };
  },
  methods: {
    logout() {
      credentialsStore.logout();
      this.$router.push('/home');
    },
  },
};
</script>
<style lang=""></style>
