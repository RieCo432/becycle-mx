<script>
import Card from '@/components/card';
import requests from '@/requests';
import DashButton from '@/components/Button/index.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'viewContract',
  components: {
    DashButton,
    Card,
  },
  data() {
    return {
      contract: {},
      client: {},
      bike: {},
      depositCollectingUser: {},
      workingUser: {},
      checkingUser: {},
      contractId: this.$route.params.contractId,
    };
  },
  methods: {
    extendContract() {
      requests.extendContract(this.contractId).then(() => {
        toast.success('Contract Extended!', {timeout: 1000});
        requests.getContract(this.contractId).then((response) => {
          this.contract = response.data;
        });
      });
    },
  },
  async created() {
    this.contract = (await requests.getContract(this.$route.params.contractId)).data;
    this.bike = (await requests.getBike(this.contract.bikeId)).data;
    this.client = (await requests.getClient(this.contract.clientId)).data;
    this.depositCollectingUser = (await requests.getUser(this.contract['depositCollectingUserId'])).data;
    this.workingUser = (await requests.getUser(this.contract['workingUserId'])).data;
    this.checkingUser = (await requests.getUser(this.contract['checkingUserId'])).data;
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <div class="grid grid-cols-12 gap-5">
        <div class="col-span-4 gap-5">
          <Card title="Lendee">
            <div class="flex flex-col h-full">
              <div class="flex-1">
                <p class="text-slate-600 dark:text-slate-300">{{client.firstName}} {{client.lastName}}</p>
                <p class="text-slate-600 dark:text-slate-300">{{client.emailAddress}}</p>
              </div>
              <DashButton @click="this.$router.push({path: `/clients/${client.id}`})">
                View Client
              </DashButton>
            </div>
          </Card>
        </div>
        <div class="col-span-4 gap-5">
          <Card title="Bike">
            <p class="text-slate-600 dark:text-slate-300">{{bike.make}} {{bike.model}}</p>
            <p class="text-slate-600 dark:text-slate-300">{{bike.colour}} {{bike.decals}}</p>
            <p class="text-slate-600 dark:text-slate-300">{{bike.serialNumber}}</p>

          </Card>
        </div>
        <div class="col-span-4 gap-5">
          <Card title="Contract">
            <div class="flex flex-col h-full">
              <div class="flex-1">
                <p class="text-slate-600 dark:text-slate-300">From: {{contract.startDate}}&emsp; Until: {{contract.endDate}}</p>
                <p class="text-slate-600 dark:text-slate-300">Notes: {{contract.notes}}</p>
                <p class="text-slate-600 dark:text-slate-300">Condition: {{contract.condition}}</p>
                <p class="text-slate-600 dark:text-slate-300">Deposit: &#163;{{contract.depositAmountCollected}} to {{depositCollectingUser.username}}</p>
                <p class="text-slate-600 dark:text-slate-300">Done by: {{workingUser.username}}</p>
                <p class="text-slate-600 dark:text-slate-300">Checked by: {{checkingUser.username}}</p>
              </div>
              <DashButton class="mt-5" @click="extendContract">
                Extend Contract
              </DashButton>
            </div>
          </Card>
        </div>
        <div class="col-span-12 gap-5">
          <Card title="Return">

          </Card>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
