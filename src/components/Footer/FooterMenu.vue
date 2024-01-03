<template lang="">
  <div
    class="bg-white bg-no-repeat custom-dropshadow footer-bg dark:bg-slate-700 flex justify-around items-center backdrop-filter backdrop-blur-[40px] fixed left-0 w-full z-[9999] bottom-0 py-[12px] px-4"
  >
    <router-link :to="{ name: 'chat' }" v-slot="{ isActive }">
      <span
        class="relative cursor-pointer rounded-full text-[20px] flex flex-col items-center justify-center"
        :class="[
          isActive ? 'text-primary-500' : 'dark:text-white text-slate-900',
        ]"
        ><Icon icon="heroicons-outline:mail" />
        <span
          class="absolute right-[5px] lg:top-0 -top-2 h-4 w-4 bg-red-500 text-[8px] font-semibold flex flex-col items-center justify-center rounded-full text-white z-[99]"
          >10</span
        >
      </span>
      <span
        class="block text-[11px]"
        :class="[
          isActive ? 'text-primary-500' : 'text-slate-600 dark:text-slate-300',
        ]"
        >Messages</span
      >
    </router-link>
    <router-link
      v-slot="{ isActive }"
      :to="{ name: 'profile' }"
      class="relative bg-white bg-no-repeat backdrop-filter backdrop-blur-[40px] rounded-full footer-bg dark:bg-slate-700 h-[65px] w-[65px] z-[-1] -mt-[40px] flex justify-center items-center"
    >
      <div
        class="h-[50px] w-[50px] rounded-full relative left-[0px] top-[0px] custom-dropshadow"
      >
        <img
          src="@/assets/images/users/user-1.jpg"
          alt=""
          class="w-full h-full rounded-full"
          :class="[
            isActive
              ? 'border-2 border-primary-500'
              : 'border-2 border-slate-100',
          ]"
        />
      </div>
    </router-link>
    <router-link :to="{ name: 'notifications' }" v-slot="{ isActive }">
      <span
        class="relative cursor-pointer rounded-full text-[20px] flex flex-col items-center justify-center"
        :class="[
          isActive ? 'text-primary-500' : 'dark:text-white text-slate-900',
        ]"
        ><Icon icon="heroicons-outline:bell" />
        <span
          class="absolute right-[17px] lg:top-0 -top-2 h-4 w-4 bg-red-500 text-[8px] font-semibold flex flex-col items-center justify-center rounded-full text-white z-[99]"
          >2</span
        >
      </span>
      <span
        class="block text-[11px]"
        :class="[
          isActive ? 'text-primary-500' : 'text-slate-600 dark:text-slate-300',
        ]"
        >Notifications</span
      >
    </router-link>
  </div>
</template>
<script>
import Icon from "@/components/Icon";
export default {
  components: {
    Icon,
  },
};
</script>
<style lang="scss"></style>
