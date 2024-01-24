<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="lg:col-span-6 col-span-12">
      <Card title="Client Login">
        <form v-if="!code_requested" @submit.prevent="requestLoginCode" class="space-y-4">
          <Textinput
            label="E-Mail Address"
            type="email"
            placeholder="E-mail Address"
            name="email"
            v-model="email_address"
            :error="emailAddressError"
            classInput="h-[48px]"
          />

          <button type="submit" class="btn btn-dark block w-full text-center">
            Continue
          </button>

        </form>

        <form v-if="code_requested" @submit.prevent="login" class="space-y-4">
          <Textinput
            label="Login Code"
            type="code"
            placeholder="6-digit code"
            name="code"
            v-model="code"
            :error="codeError"
            classInput="h-[48px]"
          />

          <button type="submit" class="btn btn-dark block w-full text-center">
            Login
          </button>

        </form>
      </Card>
    </div>
  </div>
</template>

<script>

import Card from '@/components/Card/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import requests from '@/requests';
import {useCredentialsStore} from '@/store/credentialsStore';

const credentialsStore = useCredentialsStore();

export default {
  data() {
    return {
      email_address: null,
      code_requested: false,
      client_id: null,
      code: null,
    };
  },
  methods: {
    requestLoginCode() {
      requests.getClientLoginCode(this.email_address)
          .then((response) => {
            this.client_id = response.data['id'];
            this.code_requested = true;
          });
    },
    login() {
      requests.getClientToken(this.client_id, this.code)
          .then((response) => {
            credentialsStore.login(response.data['access_token'], 'client');
            requests.getClientMe().then((response) => (credentialsStore.setName(response.data['firstName'] + ' ' + response.data['lastName'])));
            this.$router.push('/me');
          });
    },
  },
  components: {
    Card,
    Textinput,
  },
};

</script>


<style scoped lang="scss">

</style>
