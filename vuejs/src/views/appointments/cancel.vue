<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import ContractCardSkeleton from '@/components/Skeleton/ContractCardSkeleton.vue';
import Button from '@/components/Button';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'cancel',
  components: {ContractCardSkeleton, Card, Button},
  data: () => ({
    appointment: null,
    startDateTime: null,
    endDateTime: null,
  }),
  methods: {
    cancelAppointment() {
      const confirmed = confirm('Are you sure you want to cancel this appointment?');
      if (confirmed) {
        requests.cancelAppointmentViaHyperlink(this.$route.query.appointmentId, this.$route.query.clientId).then(() => {
          toast.warning('Appointment canceled', {timeout: 2000});
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
        this.$router.push({path: '/home'});
      }
    },
  },
  mounted() {
    requests.getAppointmentViaHyperlink(this.$route.query.appointmentId, this.$route.query.clientId).then((response) => {
      this.appointment = response.data;
      this.startDateTime = new Date(Date.parse(this.appointment.startDateTime));
      this.endDateTime = new Date(Date.parse(this.appointment.endDateTime));
    }).catch((error) => {
      toast.error(error.response.data.detail.description, {timeout: 2000});
      this.$router.push({path: '/home'});
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12">
    <div class="col-span-12 lg:col-span-8 lg:col-start-3">
      <Card title="Cancel Appointment">
        <div
            v-if="appointment !== null"
            class="px-6 py-8 dark:text-slate-300"
            :class="scrollContent ? 'overflow-y-auto max-h-[400px]' : ''">
          <p>Name: {{appointment.client.firstName}} {{appointment.client.lastName}}</p>
          <p>Type: {{appointment.type.title}}</p>
          <p>
            Time: {{startDateTime.getHours().toString()
              .padStart(2, '0')}}:{{startDateTime.getMinutes().toString()
              .padStart(2, '0')}} - {{endDateTime.getHours().toString()
              .padStart(2, '0')}}:{{endDateTime.getMinutes().toString()
              .padStart(2, '0')}}</p>
          <p>Confirmed: {{appointment.confirmed ? 'Yes' : 'No'}}</p>
          <p>Notes: {{appointment.notes}}</p>
          <br>
          <Button
              @click="cancelAppointment"
              text="Cancel Appointment"
          />
        </div>
        <ContractCardSkeleton v-else>
        </ContractCardSkeleton>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
