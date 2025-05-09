<script lang="ts">
import {defineComponent} from 'vue';
import requests from '@/requests';
import TextInput from '@/components/TextInput/index.vue';
import Card from '@/components/Card/index.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default defineComponent({
  name: 'clockIn',
  components: {TextInput, Card},
  data: () => {
    return {
      username: '',
      passwordOrPin: '',
      passwordOrPinError: null,
    };
  },
  methods: {
    onSubmit() {
      requests.checkUserPasswordOrPin(this.username, this.passwordOrPin)
        .then((response) => {
          toast.success('Successfully Clocked In!', {timeout: 2000});
          this.username = '';
          this.passwordOrPin = '';
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
          this.passwordOrPinError = 'Wrong password or username';
        });
    },
  },
});
</script>

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
              label="Password Or Pin"
              type="password"
              placeholder="Password"
              name="passwordOrPin"
              v-model="passwordOrPin"
              :error="passwordOrPinError"
              hasicon
              classInput="h-[48px]"
          />

          <button type="submit" class="btn btn-dark block w-full text-center">
            Clock In
          </button>
        </form>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
