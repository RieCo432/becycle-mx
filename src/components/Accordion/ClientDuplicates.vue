<template>
  <div :class="parentClass">
    <div
        class="accordion shadow-base dark:shadow-none rounded-md"
        v-for="(item, i) in items"
        :key="i"
    >
      <div
          :class="
          activeIndex === i
            ? 'bg-slate-50 dark:bg-slate-700 dark:bg-opacity-60 rounded-t-md '
            : 'bg-white dark:bg-slate-700  rounded-md'
        "
          class="flex justify-between cursor-pointer transition duration-150 font-medium w-full text-start text-base text-slate-600 dark:text-slate-300 px-8 py-4"
          @click="activeIndex = activeIndex === i ? null : i"
      >
        {{ item.client1.firstName }} {{ item.client1.lastName }} &lt;----&gt; {{ item.client2.firstName }} {{ item.client2.lastName }}

        <span
            class="text-slate-900 dark:text-white text-[22px] transition-all duration-300 h-5"
            :class="activeIndex === i ? 'rotate-180 transform' : ''"
        ><Icon icon="heroicons-outline:chevron-down"
        /></span>
      </div>
      <Transition
          enter-active-class="submenu_enter-active"
          leave-active-class="submenu_leave-active"
          @before-enter="beforeEnter"
          @enter="enter"
          @after-enter="afterEnter"
          @before-leave="beforeLeave"
          @leave="leave"
          @after-leave="afterLeave"
      >
        <div
            class="text-sm text-slate-600 font-normal bg-white dark:bg-slate-900 dark:text-slate-300 rounded-b-md"
            v-if="i === activeIndex"
            :class="[
            i === activeIndex
              ? 'dark:border dark:border-slate-700 dark:border-t-0'
              : 'l',
          ]"
        >
          <div class="px-8 py-4">
            <div class="grid grid-cols-2 gap-5">
              <div class="col-span-1">
                <Card title="Client 1">
                  <template #header>
                      <Button @click="resolvePotentialDuplicate(item.id, item.client1.id, item.client2.id)">Keep</Button>
                  </template>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300 capitalize">{{ item.client1.firstName }} {{ item.client1.lastName }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300">{{ item.client1.emailAddress }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300">Contracts: {{item.client1.contracts.length}}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300">Appointments: {{item.client1.appointments.length}}</p>
                  </div>

                </Card>
              </div>
              <div class="col-span-1">
                <Card title="Client 2">
                  <template #header>
                    <Button @click="resolvePotentialDuplicate(item.id, item.client2.id, item.client1.id)">Keep</Button>
                  </template>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300 capitalize">{{ item.client2.firstName }} {{ item.client2.lastName }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300">{{ item.client2.emailAddress }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300">Contracts: {{item.client2.contracts.length}}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300">Appointments: {{item.client2.appointments.length}}</p>
                  </div>

                </Card>
              </div>
              <div class="col-span-full">
                <Button class="block-btn" @click="ignorePotentialDuplicate(item.id)">Ignore This Potential Duplicate</Button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script>
import Icon from '@/components/Icon';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import Button from '@/components/Button/index.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'PotentialClientDuplicatesAccordion',
  components: {
    Card,
    Icon,
    Button,
  },
  emits: [
      'potentialClientDuplicateIgnored',
      'potentialClientDuplicateResolved',
  ],
  props: {
    parentClass: {
      type: String,
      default: '',
    },
    items: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      activeIndex: null,
    };
  },
  methods: {
    ignorePotentialDuplicate(clientDuplicateId) {
      requests.patchIgnorePotentialClientDuplicate(clientDuplicateId).then((response) => {
        this.$emit('potentialClientDuplicateIgnored', response.data);
        this.activeIndex = null;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    resolvePotentialDuplicate(clientDuplicateId, keepClientId, discardClientId) {
      requests.putResolvePotentialClientDuplicate(clientDuplicateId, keepClientId, discardClientId).then(() => {
        this.$emit('potentialClientDuplicateResolved', clientDuplicateId);
        this.activeIndex = null;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    beforeEnter(element) {
      requestAnimationFrame(() => {
        if (!element.style.height) {
          element.style.height = '0px';
        }

        element.style.display = null;
      });
    },
    enter(element) {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          element.style.height = `${element.scrollHeight}px`;
        });
      });
    },
    afterEnter(element) {
      element.style.height = null;
    },
    beforeLeave(element) {
      requestAnimationFrame(() => {
        if (!element.style.height) {
          element.style.height = `${element.offsetHeight}px`;
        }
      });
    },
    leave(element) {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          element.style.height = '0px';
        });
      });
    },
    afterLeave(element) {
      element.style.height = null;
    },
  },
};
</script>
