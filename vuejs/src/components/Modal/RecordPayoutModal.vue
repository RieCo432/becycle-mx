<script>
import Modal from '@/components/Modal/Modal.vue';

export default {
  name: 'RecordPayoutModal',
  components: {Modal},
  emits: ['close'],
  props: {
    activeModal: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
  },
};
</script>

<template>
  <Modal :active-modal="activeModal" @close="closeModal" title="Record Payout"></Modal>
</template>

<style scoped lang="scss">

</style>
