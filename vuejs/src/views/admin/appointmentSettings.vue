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
    <div class="col-span-12 xl:col-span-4">
      <EditAppointmentGeneralSettingsCard></EditAppointmentGeneralSettingsCard>
    </div>
    <div class="col-span-12 xl:col-span-8">
      <EditAppointmentConcurrencySettingsCard></EditAppointmentConcurrencySettingsCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
