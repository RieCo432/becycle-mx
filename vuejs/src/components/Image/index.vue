<template>
  <div class="relative" :class="parentClass">
    <img
      :src="src"
      :alt="alt"
      v-if="src"
      :class="imageClass"
      class="max-w-full block"
    />
    <div
      v-if="!src"
      class="bg-neutral-300 w-full h-[200px] flex flex-col items-center justify-center font-medium rounded-md text-xl text-slate-900 capitalize"
    >
      Please Set Image
      <code class="text-sm text-primary-500 lowercase mt-3">
        [src="images/all-img/image-1.png"]
      </code>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    src: {
      type: String,
      required: true,
    },
    alt: {
      type: String,
      default: 'image title',
    },
    imageClass: {
      type: String,
      default: '',
    },
    parentClass: {
      type: String,
      default: '',
    },
  },
};
</script>
<style lang=""></style>
