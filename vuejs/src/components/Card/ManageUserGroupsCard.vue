<script lang="ts">
import {defineComponent, ref} from 'vue';
import DashButton from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default defineComponent({
  name: 'ManageUserGroupsCard',
  components: {TextInput, Card, DashButton},
  props: {
    user: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const userGroups = ref([]);

    const newUserGroupSchema = yup.object().shape({
      newUserGroupName: yup.string().max(50).required(),
    });

    const {handleSubmit: handleNewUserGroupSubmit} = useForm({
      validationSchema: newUserGroupSchema,
      keepValuesOnDismount: true,
    });

    const {value: newUserGroupName, errorMessage: newUserGroupNameError,
      resetField: resetNewUserGroupName} = useField('newUserGroupName');

    const submitNewUserGroup = handleNewUserGroupSubmit(() => {
      requests.postUserGroup(newUserGroupName.value).then((response) => {
        userGroups.value.push(response.data);
        resetNewUserGroupName();
        toast.success('User Group created', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      userGroups,
      newUserGroupName,
      newUserGroupNameError,
      submitNewUserGroup,
    };
  },
  methods: {
    deleteUserGroup(userGroupId) {
      requests.deleteUserGroup(userGroupId)
        .then((response) => {
          const indexInArray = this.userGroups.findIndex((t) => (t.id === response.data.id));
          this.userGroups.splice(indexInArray, 1);
          toast.success('User Group deleted', {timeout: 2000});
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    },
  },
  mounted() {
    requests.getUserGroups().then((response) => {
      this.userGroups = response.data;
    });
  },
});
</script>

<template>
  <Card title="Manage User Groups">
    <div class="grid grid-cols-12 gap-2">
      <div class="col-span-10">
        <span class="text-slate-700 dark:text-slate-300 text-xl">Group Name</span>
      </div>
      <div class="col-span-2">
        <span class="text-slate-700 dark:text-slate-300 text-xl">Action</span>
      </div>
      <template v-for="userGroup in userGroups" :key="userGroup.id">
        <div class="col-span-10">
          <span class="text-slate-700 dark:text-slate-300">{{userGroup.name}}</span>
        </div>
        <div class="col-span-2">
          <DashButton
              v-if="user.admin"
              @click="deleteUserGroup(userGroup.id)"
              class="bg-danger-500 dark:bg-danger-600 btn-sm mx-auto block-btn"
              icon="heroicons-outline:trash"/>
        </div>
      </template>
    </div>
    <form v-if="user.admin" @submit.prevent="submitNewUserGroup">
      <div class="grid grid-cols-12 gap-2 mt-2">
        <div class="col-span-10">
          <TextInput
              type="text"
              placeholder="New User Group Name"
              name="newUserGroupName"
              v-model="newUserGroupName"
              :error="newUserGroupNameError"
          />
        </div>
        <div class="col-span-2">
          <DashButton type="submit" class="btn-sm mx-auto block-btn" icon="heroicons-outline:plus"/>
        </div>
      </div>
    </form>
  </Card>
</template>

<style scoped lang="scss">

</style>
