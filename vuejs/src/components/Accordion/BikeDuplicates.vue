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
          class="flex justify-between cursor-pointer transition duration-150 font-medium w-full text-start
                 text-base text-slate-600 dark:text-slate-300 px-8 py-4"
          @click="activeIndex = activeIndex === i ? null : i"
      >
        {{ item.bike1.make }} {{ item.bike1.model }} &lt;----&gt; {{ item.bike2.make }} {{ item.bike2.model }}

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
                <Card title="Bike 1">
                  <template #header>
                    <Button @click="viewBike(item.bike1.id)">View</Button>
                    <Button @click="resolvePotentialDuplicate(item.id, item.bike1.id, item.bike2.id)" class="ml-5">Keep</Button>
                  </template>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300 capitalize">{{ item.bike1.make }} {{ item.bike1.model }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300 capitalize">Colour: {{ item.bike1.colour }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300 capitalize">Decals: {{ item.bike1.decals }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300">Serial Number: {{ item.bike1.serialNumber }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300">Contracts: {{item.bike1.contracts.length}}</p>
                  </div>

                </Card>
              </div>
              <div class="col-span-1">
                <Card title="Bike 2">
                  <template #header>
                    <Button @click="viewBike(item.bike2.id)">View</Button>
                    <Button @click="resolvePotentialDuplicate(item.id, item.bike2.id, item.bike1.id)" class="ml-5">Keep</Button>
                  </template>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300 capitalize">{{ item.bike2.make }} {{ item.bike2.model }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300 capitalize">Colour: {{ item.bike2.colour }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300 capitalize">Decals: {{ item.bike2.decals }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300">Serial Number: {{ item.bike2.serialNumber }}</p>
                  </div>
                  <div class="col-span-full">
                    <p class="text-base text-slate-700 dark:text-slate-300">Contracts: {{item.bike2.contracts.length}}</p>
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
  name: 'PotentialBikeDuplicatesAccordion',
  components: {
    Card,
    Icon,
    Button,
  },
  emits: [
    'potentialBikeDuplicateIgnored',
    'potentialBikeDuplicateResolved',
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
    ignorePotentialDuplicate(bikeDuplicateId) {
      requests.patchIgnorePotentialBikeDuplicate(bikeDuplicateId).then((response) => {
        this.$emit('potentialBikeDuplicateIgnored', response.data);
        this.activeIndex = null;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    resolvePotentialDuplicate(bikeDuplicateId, keepBikeId, discardBikeId) {
      requests.putResolvePotentialBikeDuplicate(bikeDuplicateId, keepBikeId, discardBikeId).then(() => {
        this.$emit('potentialBikeDuplicateResolved', bikeDuplicateId);
        this.activeIndex = null;
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    viewBike(bikeId) {
      const routeData = this.$router.resolve({path: `/bikes/${bikeId}`});
      window.open(routeData.href, '_blank');
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
