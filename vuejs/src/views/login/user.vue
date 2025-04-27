<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="lg:col-span-6 col-span-12">
      <Card title="Volunteer Login">
        <form @submit.prevent="onSubmit" class="space-y-4">
          <TextInput
            label="Username"
            type="username"
            placeholder="username"
            name="username"
            v-model="username"
            classInput="h-[48px]"
          />
          <TextInput
            label="Password"
            type="password"
            placeholder="Password"
            name="password"
            v-model="password"
            :error="passwordError"
            hasicon
            classInput="h-[48px]"
          />

          <button type="submit" class="btn btn-dark block w-full text-center">
            Sign in
          </button>
        </form>
      </Card>
    </div>
  </div>
</template>


<script>

import requests from '@/requests';
import TextInput from '@/components/TextInput/index.vue';
import Card from '@/components/Card/index.vue';
import {useCredentialsStore} from '@/store/credentialsStore';
import {useToast} from 'vue-toastification';

const credentialsStore = useCredentialsStore();
const toast = useToast();

export default {
  data: () => {
    return {
      username: '',
      password: '',
      passwordError: null,
    };
  },
  methods: {
    onSubmit() {
      requests.getUserToken(this.username, this.password)
        .then((response) => {
          credentialsStore.login(response.data['access_token'], 'user');
          requests.getUserMe().then((response) => {
            credentialsStore.setName(response.data['username']);
            this.$router.push('/me');
          });
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          this.passwordError = 'Wrong password or username';
        });
    },
  },
  components: {
    Card,
    TextInput,
  },
};

</script>


<style scoped lang="scss">

</style>
