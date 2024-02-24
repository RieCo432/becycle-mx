<script>
import EditAppointmentGeneralSettingsCard from '@/components/Card/EditAppointmentGeneralSettingsCard.vue';
import EditAppointmentConcurrencySettingsCard from '@/components/Card/EditAppointmentConcurrencySettingsCard.vue';
export default {
  name: 'appointmentSettings',
  components: {
    EditAppointmentGeneralSettingsCard,
    EditAppointmentConcurrencySettingsCard,
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-6">
      <EditAppointmentGeneralSettingsCard></EditAppointmentGeneralSettingsCard>
    </div>
    <div class="col-span-6">
      <EditAppointmentConcurrencySettingsCard></EditAppointmentConcurrencySettingsCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>