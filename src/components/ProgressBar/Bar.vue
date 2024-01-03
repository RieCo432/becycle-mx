<template>
  <Transition appear @before-appear="beforeEnter" @after-appear="enter">
    <div
      class="flex flex-col text-center whitespace-nowrap justify-center h-full"
      :class="`${barColor} ${animate ? 'animated-strip' : ''}`"
    >
      <span v-if="showValue" class="text-[10px] text-white font-bold">{{
        value + "%"
      }}</span>
    </div>
  </Transition>
</template>
<script>
export default {
  props: {
    value: {
      type: Number,
      default: 50,
    },

    barColor: {
      type: String,
      default: "bg-slate-900",
    },
    showValue: {
      type: Boolean,
      default: false,
    },
    striped: {
      type: Boolean,
      default: false,
    },
    animate: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    beforeEnter(el) {
      el.style.width = 0;
    },
    enter(el) {
      el.style.width = `${this.value}%`;
      el.style.transition = `width 1s linear`;
      // add backgroudn image
      if (this.striped === true) {
        el.style.backgroundImage =
          "linear-gradient(45deg,hsla(0,0%,100%,.15) 25%,transparent 0,transparent 50%,hsla(0,0%,100%,.15) 0,hsla(0,0%,100%,.15) 75%,transparent 0,transparent)";

        el.style.backgroundSize = ".857rem .857rem";
      }
    },
  },
};
</script>
<style lang="scss" scoped>
@keyframes progress-bar-stripes {
  0% {
    background-position: 1rem 0;
  }
  to {
    background-position: 0 0;
  }
}
.animated-strip {
  animation: progress-bar-stripes 1s linear infinite;
}
</style>
