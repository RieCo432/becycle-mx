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
        {{ item.title }}

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
            {{ item.content }}
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script>
import Icon from "@/components/Icon";
export default {
  components: {
    Icon,
  },
  props: {
    parentClass: {
      type: String,
      default: "",
    },
    items: {
      type: Array,
      required: true,
      // setr default value for items

      default: () => [
        {
          title: "How does Dashcode work?",
          content:
            "Jornalists call this critical, introductory section the  and when bridge properly executed, it's the that carries your reader from anheadine try at attention-grabbing to the body of your blog post.",
        },
        {
          title: "Where i can learn more about using Dashcode?",
          content:
            "Jornalists call this critical, introductory section the  and when bridge properly executed, it's the that carries your reader from anheadine try at attention-grabbing to the body of your blog post.",
        },
        {
          title: "Why Dashcode is so important?",
          content:
            "Jornalists call this critical, introductory section the  and when bridge properly executed, it's the that carries your reader from anheadine try at attention-grabbing to the body of your blog post.",
        },
      ],
    },
  },
  data() {
    return {
      activeIndex: 0,
    };
  },
  methods: {
    beforeEnter(element) {
      requestAnimationFrame(() => {
        if (!element.style.height) {
          element.style.height = "0px";
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
          element.style.height = "0px";
        });
      });
    },
    afterLeave(element) {
      element.style.height = null;
    },
  },
};
</script>
