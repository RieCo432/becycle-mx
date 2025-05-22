<script lang="ts">
import {defineComponent, ref} from 'vue';
import DashButton from '@/components/Button/index.vue';
import Card from '@/components/Card/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import UserPermissionScopeTree from '@/components/UserPermissionScopeTree/UserPermissionScopeTree.vue';
import SetNewPasswordModal from '@/components/Modal/SetNewPasswordModal.vue';

const toast = useToast();

export default defineComponent({
  name: 'ManageUserGroupsCard',
  components: {SetNewPasswordModal, UserPermissionScopeTree, TextInput, Card, DashButton},
  props: {
    user: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const userGroups = ref([]);
    const permissionScopes = ref({});

    const groupPermissions = ref([]);

    const addGroupPermission = (permissionScopeId) => {
      groupPermissions.value.push(permissionScopeId);
    };

    const removeGroupPermission = (permissionScopeIds) => {
      permissionScopeIds.forEach((permissionScopeId) => {
        const indexInArray = groupPermissions.value.indexOf(permissionScopeId);
        if (indexInArray !== -1) {
          groupPermissions.value.splice(indexInArray, 1);
        }
      });
    };

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
      groupPermissions,
      permissionScopes,
      addGroupPermission,
      removeGroupPermission,
    };
  },
  data() {
    return {
      showEditGroupPermissionsModal: false,
      editGroupPermissionsModalInfo: {
        username: '',
        id: '',
      },
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
    openEditGroupPermissionsModal(groupId) {
      requests.getGroupPermissions(groupId).then((response) => {
        this.groupPermissions.splice(0, this.groupPermissions.length);
        response.data.forEach((groupPermission) => {
          this.groupPermissions.push(groupPermission.id);
        });
        this.showEditGroupPermissionsModal = !this.showEditGroupPermissionsModal;
        const group = this.userGroups[this.userGroups.findIndex((group) => group.id === groupId)];
        this.editGroupPermissionsModalInfo = {
          id: group.id,
          username: group.name,
        };
        console.log('pulled permissions', this.groupPermissions);
      });
    },
  },
  mounted() {
    requests.getUserGroups().then((response) => {
      this.userGroups = response.data;
    });
    requests.getPermissionScopes().then((response) => {
      this.permissionScopes = response.data;
    });
  },
});
</script>

<template>
  <Card title="Manage User Groups">
    <div class="grid grid-cols-12 gap-2">
      <div class="col-span-8">
        <span class="text-slate-700 dark:text-slate-300 text-xl">Group Name</span>
      </div>
      <div class="col-span-4">
        <span class="text-slate-700 dark:text-slate-300 text-xl">Action</span>
      </div>
      <template v-for="userGroup in userGroups" :key="userGroup.id">
        <div class="col-span-8">
          <span class="text-slate-700 dark:text-slate-300">{{userGroup.name}}</span>
        </div>
        <div class="col-span-2">
          <DashButton
              v-if="user.admin"
              @click="openEditGroupPermissionsModal(userGroup.id)"
              class="btn-sm mx-auto block-btn"
              icon="heroicons-outline:pencil-square"/>
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
        <div class="col-span-8">
          <TextInput
              type="text"
              placeholder="New User Group Name"
              name="newUserGroupName"
              v-model="newUserGroupName"
              :error="newUserGroupNameError"
          />
        </div>
        <div class="col-span-2 col-end-13">
          <DashButton type="submit" class="btn-sm mx-auto block-btn" icon="heroicons-outline:plus"/>
        </div>
      </div>
    </form>
  </Card>
  <SetNewPasswordModal
      size-class="w-3/4"
      :active-modal="showEditGroupPermissionsModal"
      :user-info="editGroupPermissionsModalInfo"
      title="Edit User Permissions"
      @close="showEditGroupPermissionsModal = !showEditGroupPermissionsModal">
    <div class="grid grid-cols-12">
      <div class="col-span-1"></div>
      <div class="col-span-8">Route</div>
      <div class="col-span-3 grid grid-cols-5">
        <div class="col-span-1 text-center" v-for="method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']" :key="method">{{method}}</div>
      </div>
      <UserPermissionScopeTree
          :tree="permissionScopes"
          :user-permissions="groupPermissions"
          :group-id="editGroupPermissionsModalInfo.id"
          @user-permission-added="addGroupPermission"
          @user-permission-removed="removeGroupPermission"
      ></UserPermissionScopeTree>
    </div>
  </SetNewPasswordModal>
</template>

<style scoped lang="scss">

</style>
