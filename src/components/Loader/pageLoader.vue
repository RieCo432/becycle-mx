<template>
  <div class="h-20 w-20 mx-auto" v-if="!isLoading">
    <img src="@/assets/images/svg/loader.svg" alt="" />
  </div>
</template>
<script>
export default {
  name: "LoaderElement",
  data() {
    return {
      isLoading: false,
    };
  },
  mounted() {
    // onreadystatechange
    document.onreadystatechange = () => {
      if (document.readyState === "complete") {
        this.isLoading = true;
      }
    };
  },
};
</script>
<style lang=""></style>
