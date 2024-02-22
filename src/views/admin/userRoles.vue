<script>
import UserRolesTable from '@/components/Tables/UserRolesTable.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';

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
    patchUser(userId, patchData) {
      requests.patchUser(userId, patchData).then((response) => {
        const indexInArray = this.userData.findIndex((user) => (user.id === response.data.id));
        this.userData[indexInArray].admin = response.data.admin;
      });
    },
  },
  created() {
    requests.getUsers().then((response) => {
      this.userData = response.data;
      this.loadingUsers = false;
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12">
      <Card>
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <UserRolesTable :loading="loadingUsers" :actions="userActions" :columns="userColumns" :table-data="userData" title="Users" :patch-user="patchUser"></UserRolesTable>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>