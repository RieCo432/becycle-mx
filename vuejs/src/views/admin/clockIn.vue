<script lang="ts">
import {defineComponent} from 'vue';
import requests from '@/requests';
import TextInput from '@/components/TextInput/index.vue';
import Card from '@/components/Card/index.vue';
import {useToast} from 'vue-toastification';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';

const toast = useToast();

export default defineComponent({
  name: 'clockIn',
  components: {ComboboxTextInput, TextInput, Card},
  data: () => {
    return {
      username: null,
      passwordOrPin: null,
      passwordOrPinError: null,
      userSelectionOptionsStatic: true,
      activeUsers: [],
    };
  },
  computed: {
    filtered_username_suggestions() {
      return this.activeUsers
        .filter((suggestion) =>
          this.username === null ||
          suggestion
            .toLowerCase()
            .startsWith(this.username.toLowerCase()))
        .sort(this.userSortingFunction)
        .slice(0, 10);
    },
  },
  mounted() {
    requests.getActiveUsers().then((response) => (this.activeUsers = response.data.map((user) => (user.username))));
  },
  methods: {
    userSortingFunction(user1, user2) {
      if (user1.toLowerCase() > user2.toLowerCase()) return 1;
      if (user1.toLowerCase() < user2.toLowerCase()) return -1;
      return 0;
    },
    selectUser(event, i) {
      if (i !== -1) {
        this.username = this.filtered_username_suggestions[i];
        this.userSelectionOptionsStatic = false;
        this.passwordOrPin = null;
        this.passwordOrPinError = null;
      }
    },
    onSubmit() {
      requests.checkUserPasswordOrPin(this.username, this.passwordOrPin)
        .then((response) => {
          if (response.data) {
            toast.success('Successfully Clocked In!', {timeout: 2000});
            this.username = null;
            this.passwordOrPin = null;
            this.passwordOrPinError = null;
            this.userSelectionOptionsStatic = true;
          } else {
            toast.error('Incorrect Password Or Pin', {timeout: 2000});
            this.passwordOrPinError = 'Incorrect Password Or Pin';
            this.passwordOrPin = null;
          }
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    },
  },
});
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="lg:col-span-6 lg:col-start-4 col-span-12">
      <Card title="Volunteer Clock-In">
        <form @submit.prevent="onSubmit" class="space-y-4">
          <ComboboxTextInput
              :field-model-value="username"
              :suggestions="filtered_username_suggestions"
              :selected-callback="selectUser"
              :allow-new="false"
              :open-by-default="userSelectionOptionsStatic"
              label="Volunteer"
              type="text"
              placeholder="workshop"
              name="workingUser"
              v-model="username"
              @input="() => {}"
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
