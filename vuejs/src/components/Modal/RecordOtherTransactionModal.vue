<script>
import Modal from '@/components/Modal/Modal.vue';

export default {
  name: 'RecordOtherTransactionModal',
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
  <Modal :active-modal="activeModal" @close="closeModal" title="Record Other Transaction">
    <div class="grid grid-cols-12 gap-5">
      <div class="col-span-full">
        <span class="text-danger-500">Danger Zone! Do not fuck around!</span>
      </div>
    </div>
  </Modal>
</template>

<style scoped lang="scss">

</style>
