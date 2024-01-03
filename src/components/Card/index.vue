<template>
  <div
    :class="`card rounded-md bg-white dark:bg-slate-800 lg:h-full  ${
      this.$store.themeSettingsStore.skin === 'bordered'
        ? ' border border-gray-5002 dark:border-slate-700'
        : 'shadow-base'
    }
   
    ${className}
    
    `"
    v-if="!overlay"
  >
    <div class="card-body flex flex-col" :class="bodyClass">
      <header
        v-if="title || subtitle"
        class="flex mb-5 items-center"
        :class="`
      ${imgTop ? 'order-1' : ''}
      ${
        noborder
          ? ''
          : 'border-b border-slate-100 dark:border-slate-700 pb-5  -mx-6 px-6'
      }
      
      `"
      >
        <div class="flex-1">
          <div
            class="card-title text-slate-900 dark:text-white"
            v-if="title"
            :class="titleClass"
          >
            {{ title }}
          </div>
          <div v-if="subtitle" class="card-subtitle" :class="subtitleClass">
            {{ subtitle }}
          </div>
        </div>
        <div class="flex-0" v-if="$slots.header">
          <slot name="header"></slot>
        </div>
      </header>
      <div
        class="image-box"
        v-if="img"
        :class="`
        ${imgTop ? 'order-0' : ''}
        ${gapNull ? '-mx-6 ' : ''}
        ${gapNull && imgTop ? '-mt-6 ' : ''}
        ${gapNull && imgBottom ? '-mb-6 ' : ''}
        
        ${imgBottom ? 'order-3 mt-6' : ' mb-6'}
        
        
        `"
      >
        <img
          :src="img"
          alt=""
          class="block w-full h-full object-cover"
          :class="imaClass"
        />
      </div>

      <div :class="imgTop ? 'order-2' : ''" class="card-text h-full">
        <slot></slot>
      </div>
    </div>
  </div>
  <div
    class="rounded-md overlay bg-no-repeat bg-center bg-cover card"
    :class="className"
    v-if="overlay"
    :style="{
      backgroundImage: 'url(' + `${img}` + ')',
    }"
  >
    <div
      class="card-body h-full flex flex-col justify-center"
      :class="bodyClass"
    >
      <header class="mb-5">
        <div
          class="card-title text-slate-900 dark:text-white"
          v-if="title"
          :class="titleClass"
        >
          {{ title }}
        </div>
        <div v-if="subtitle" class="card-subtitle" :class="subtitleClass">
          {{ subtitle }}
        </div>
      </header>
      <div class="card-text h-full">
        <slot></slot>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'Card',
  props: {
    className: {
      type: String,
      default: '',
    },
    title: {
      type: String,
      default: '',
    },
    titleClass: {
      type: String,
      default: '',
    },
    subtitle: {
      type: String,
      default: '',
    },
    subtitleClass: {
      type: String,
      default: '',
    },
    img: {
      type: String,
      default: '',
    },
    imaClass: {
      type: String,
      default: '',
    },
    imgTop: {
      type: Boolean,
      default: false,
    },
    imgBottom: {
      type: Boolean,
      default: false,
    },
    gapNull: {
      type: Boolean,
      default: false,
    },
    overlay: {
      type: Boolean,
      default: false,
    },
    noborder: {
      type: Boolean,
      default: false,
    },
    bodyClass: {
      type: String,
      default: 'p-6',
    },
  },
};
</script>
<style lang="scss" scoped>
.card-title {
  @apply font-medium  capitalize md:text-xl md:leading-[28px] text-lg leading-[24px];
}
.card-subtitle {
  @apply text-sm leading-5 font-medium text-slate-600 dark:text-slate-300 mt-1;
}
.overlay {
  @apply relative z-[1] after:absolute after:inset-0 after:w-full after:h-full after:bg-slate-900 after:bg-opacity-40 after:rounded-md after:z-[-1];
  .card-title,
  .card-subtitle {
    @apply text-white;
  }
}
</style>
