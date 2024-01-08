<template>
  <form @submit.prevent="onSubmit" class="space-y-4">
    <Textinput
        label="Username"
        type="username"
        placeholder="username"
        name="emil"
        v-model="username"
        :error="usernameError"
        classInput="h-[48px]"
    />
    <Textinput
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
</template>


<script>

import requests from '@/requests';
import Textinput from '@/components/Textinput/index.vue';

export default {
  data: () => {
    return {
      username: '',
      password: '',
    };
  },
  methods: {
    onSubmit() {
      requests.getUserToken(this.username, this.password)
          .then((response) => {
            localStorage.setItem('token', response.data['access_token']);
            localStorage.setItem('tokenType', 'user');
            requests.getUserMe().then((res) => (
              localStorage.setItem('name', res.data['username'])));
            this.$router.push('/user/me');
          });
    },
  },
  components: {
    Textinput,
  },
};

</script>


<style scoped lang="scss">

</style>
