<script>
import Card from '@/components/Card/index.vue';
import Button from '@/components/Button/index.vue';
import RecordRevenueModal from '@/components/Modal/RecordRevenueModal.vue';
import RecordPayoutModal from '@/components/Modal/RecordPayoutModal.vue';
import RecordTransferModal from '@/components/Modal/RecordTransferModal.vue';
import RecordOtherTransactionModal from '@/components/Modal/RecordOtherTransactionModal.vue';

export default {
  name: 'fundTransfers',
  components: {RecordOtherTransactionModal, Card, Button, RecordRevenueModal, RecordPayoutModal, RecordTransferModal},
  data() {
    return {
      showRecordRevenueModal: false,
      showRecordPayoutModal: false,
      showRecordTransferModal: false,
      showRecordOtherTransactionModal: false,
    };
  },
  methods: {
    openRecordRevenueModal() {
      this.showRecordRevenueModal = true;
    },
    openRecordPayoutModal() {
      this.showRecordPayoutModal = true;
    },
    openRecordTransferModal() {
      this.showRecordTransferModal = true;
    },
    openRecordOtherTransactionModal() {
      this.showRecordOtherTransactionModal = true;
    },
    closeRecordRevenueModal() {
      this.showRecordRevenueModal = false;
    },
    closeRecordPayoutsModal() {
      this.showRecordPayoutModal = false;
    },
    closeRecordTransferModal() {
      this.showRecordTransferModal = false;
    },
    closeRecordOtherTransactionModal() {
      this.showRecordOtherTransactionModal = false;
    },
  },
};
</script>

<template>
  <div>
    <Card title="Record Transaction">
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-3">
          <Button
            text="Record Revenue"
            @click="openRecordRevenueModal"
          />
        </div>
        <div class="col-span-3">
          <Button
            text="Record Payout"
            @click="openRecordPayoutModal"
          />
        </div>
        <div class="col-span-3">
          <Button
            text="Record Transfer"
            @click="openRecordTransferModal"
          />
        </div>
        <div class="col-span-3">
          <Button
            text="Record Other Transaction"
            @click="openRecordOtherTransactionModal"
          />
        </div>
      </div>
    </Card>
    <RecordRevenueModal :active-modal="showRecordRevenueModal" @close="closeRecordRevenueModal"/>
    <RecordPayoutModal :active-modal="showRecordPayoutModal" @close="closeRecordPayoutsModal"/>
    <RecordTransferModal :active-modal="showRecordTransferModal" @close="closeRecordTransferModal"/>
    <RecordOtherTransactionModal :active-modal="showRecordOtherTransactionModal" @close="closeRecordOtherTransactionModal"/>
  </div>
</template>

<style scoped lang="scss">

</style>
