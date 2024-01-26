<script>
import clientView from '@/views/client/clientView.vue';
export default {
  name: 'clientIndex',
  components: {
    clientView,
  },
  created() {
    console.log();
  },
};
</script>

<template>
  <div>
    <client-view id="{{$route.params.id}}"></client-view>
  </div>
</template>

<style scoped lang="scss">

</style>
