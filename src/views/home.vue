<template>
    <div class="grid grid-cols-12 gap-5">
        <div class="lg:col-span-8 col-span-12">
            <Card title="Welcome to beCyCle">
                <div class="grid grid-cols-12 h-full gap-5">
                  <div class="col-span-12">
                    <p class="text-base text-slate-700 dark:text-slate-300">This is the official website for beCyCle, the community bicycle library and workshop in Aberdeen</p>
                  </div>
                  <div v-if="isNotUser" class="md:col-span-4 col-span-6 mt-auto">
                    <DashButton  @click="goToBookAppointment" class="mt-auto">Book Appointment</DashButton>
                  </div>
                  <div v-if="isNotUser && isNotClient" class="md:col-span-4 col-span-6 mt-auto">
                    <DashButton  @click="goToClientLogin" class="mt-auto">Client Login</DashButton>
                  </div>
                  <div v-if="!isNotUser" class="md:col-span-4 col-span-6 mt-auto">
                    <DashButton  @click="goToNewContract" class="mt-auto">New Contract</DashButton>
                  </div>
                  <div v-if="!isNotUser" class="md:col-span-4 col-span-6 mt-auto">
                    <DashButton  @click="goToFindClient" class="mt-auto">Find Client</DashButton>
                  </div>
                </div>

            </Card>
        </div>
        <div class="lg:col-span-4 col-span-12">
            <Card title="Opening Times" v-if="!loading">
                <vue-good-table
                  :columns="columns"
                  :rows="openingTimes"
                  style-class="vgt-table"
                  :sort-options="{
                    enabled: false
                  }"/>
            </Card>
        </div>
    </div>
</template>

<script>
import requests from '@/requests';
import Card from '@/components/Card';
import DashButton from '@/components/Button/index.vue';
import {useCredentialsStore} from '@/store/credentialsStore';

const credentialsStore = useCredentialsStore();

export default {
  components: {
    DashButton,
    Card,
  },
  data() {
    return {
      loading: true,
      openingTimes: null,
      columns: [
        {
          label: 'Day',
          field: 'day',
        },
        {
          label: 'Open',
          field: 'open',
        },
        {
          label: 'Close',
          field: 'close',
        },
      ],
    };
  },
  computed: {
    isNotUser() {
      return credentialsStore.getTokenType() !== 'user';
    },
    isNotClient() {
      return credentialsStore.getTokenType() !== 'client';
    },
  },
  methods: {
    goToBookAppointment() {
      this.$router.push({path: '/appointments/book'});
    },
    goToClientLogin() {
      this.$router.push({path: '/clients/login'});
    },
    goToNewContract() {
      this.$router.push({path: '/contracts/new'});
    },
    goToFindClient() {
      this.$router.push({path: '/clients'});
    },
  },
  mounted() {
    requests.getOpeningTimes().then((response) => {
      this.openingTimes = response.data;
      this.loading = false;
    });
  },
};

</script>
<style lang=""></style>
