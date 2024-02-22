<script>
import UserRolesTable from '@/components/Tables/UserRolesTable.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'userRoles',
  components: {Card, UserRolesTable},
  data() {
    return {
      loadingUsers: true,
      userActions: [],
      userColumns: [
        {
          label: 'Username',
          field: 'username',
        },
        {
          label: 'Admin',
          field: 'admin',
        },
        {
          label: 'Deposit Bearer',
          field: 'depositBearer',
        },
        {
          label: 'Rental Checker',
          field: 'rentalChecker',
        },
        {
          label: 'Appointment Manager',
          field: 'appointmentManager',
        },
        {
          label: 'Treasurer',
          field: 'treasurer',
        },
        {
          label: 'Soft Deleted',
          field: 'softDeleted',
        },
      ],
      userData: [],
    };
  },
  methods: {
    patchUser(userId, patchData, failureCallback) {
      requests.patchUser(userId, patchData)
          .then((response) => {
            const indexInArray = this.userData.findIndex((user) => (user.id === userId));
            this.userData.splice(indexInArray, 1, response.data);
          })
          .catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 2000});
            failureCallback();
          });
    },
    getUserData() {
      this.loadingUsers = true;
      requests.getUsers().then((response) => {
        this.userData = response.data.sort((a, b) => (a.softDeleted - b.softDeleted || b.username - a.username));
        this.loadingUsers = false;
      });
    },
  },
  created() {
    this.getUserData();
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="2xl:col-span-9 col-span-12">
      <Card>
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <UserRolesTable :loading="loadingUsers" :actions="userActions" :columns="userColumns" :table-data="userData" title="Users" :patch-user="patchUser"></UserRolesTable>
          </div>
        </div>
      </Card>
    </div>
    <div class="2xl:col-span-3 col-span-12">
      <Card>
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            Add User
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>