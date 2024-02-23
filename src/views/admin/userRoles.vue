<script>
import UserRolesTable from '@/components/Tables/UserRolesTable.vue';
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import Textinput from '@/components/Textinput/index.vue';
import Checkbox from '@/components/Switch/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {ref} from 'vue';
import Button from '@/components/Button';
import SetNewPasswordModal from '@/components/Modal/SetNewPasswordModal.vue';

const toast = useToast();

export default {
  name: 'userRoles',
  components: {Checkbox, Textinput, Card, UserRolesTable, Button, SetNewPasswordModal},
  setup() {
    const userData = ref([]);
    const showSetNewPasswordModal = ref(false);
    const setNewPasswordModalInfo = ref({
      id: null,
      username: null,
    });
    const showSetNewPinModal = ref(false);
    const setNewPinModalInfo = ref({
      id: null,
      username: null,
    });

    const newUserSchema = yup.object().shape({
      username: yup.string().required('Username is required').notOneOf(userData.value.map((user) => (user.username)), 'This username exists already!'),
      password: yup
          .string()
          .required('Password is required'),
      confirmPassword: yup
          .string()
          .required('Confirm Password is required')
          .oneOf([yup.ref('password')], 'Passwords must match'),
      pin: yup.string().matches(/^[0-9]{4}$/, 'Must be exactly 4 digits'),
      confirmPin: yup.string().oneOf([yup.ref('pin')], 'PINs must match'),
    });

    const admin = ref(false);
    const depositBearer = ref(false);
    const rentalChecker = ref(false);
    const appointmentManager = ref(false);
    const treasurer = ref(false);

    const {handleSubmit: handleNewUserSubmit} = useForm({
      validationSchema: newUserSchema,
      keepValuesOnUnmount: true,
    });

    const {value: username, errorMessage: usernameError} = useField('username');
    const {value: password, errorMessage: passwordError} = useField('password');
    const {value: confirmPassword, errorMessage: confirmPasswordError} = useField('confirmPassword');
    const {value: pin, errorMessage: pinError} = useField('pin');
    const {value: confirmPin, errorMessage: confirmPinError} = useField('confirmPin');


    const postNewUser = handleNewUserSubmit(() => {
      console.log(username.value, password.value, pin.value, admin.value, depositBearer.value,
          rentalChecker.value, appointmentManager.value, treasurer.value);
      requests.postNewUser(username.value, password.value, pin.value, admin.value, depositBearer.value,
          rentalChecker.value, appointmentManager.value, treasurer.value).then((response) => {
        toast.success('User created!', {timeout: 2000});
        userData.value.push(response.data);
      });
    });

    const newPasswordSchema = yup.object().shape({
      newPassword: yup
          .string()
          .required('Password is required'),
      confirmNewPassword: yup
          .string()
          .required('Confirm Password is required')
          .oneOf([yup.ref('newPassword')], 'Passwords must match'),
    });

    const {handleSubmit: handleNewPasswordSubmit, resetForm: resetNewPasswordForm} = useForm({
      validationSchema: newPasswordSchema,
      keepValuesOnUnmount: true,
    });

    const {value: newPassword, errorMessage: newPasswordError} = useField('newPassword');
    const {value: confirmNewPassword, errorMessage: confirmNewPasswordError} = useField('confirmNewPassword');


    const patchNewPassword = handleNewPasswordSubmit(() => {
      const userId = setNewPasswordModalInfo.value.id;
      requests.patchUser(userId, {passwordCleartext: newPassword.value}).then((response) => {
        const indexInArray = userData.value.findIndex((user) => (user.id === userId));
        userData.value.splice(indexInArray, 1, response.data);
        toast.success('Password changed!', {timeout: 2000});
      }).finally(() => {
        resetNewPasswordForm();
        showSetNewPasswordModal.value = !showSetNewPasswordModal.value;
      });
    });


    const newPinSchema = yup.object().shape({
      newPin: yup.string().matches(/^[0-9]{4}$/, 'Must be exactly 4 digits'),
      confirmNewPin: yup.string().oneOf([yup.ref('newPin')], 'PINs must match'),
    });


    const {handleSubmit: handleNewPinSubmit, resetForm: resetNewPinForm} = useForm({
      validationSchema: newPinSchema,
      keepValuesOnUnmount: true,
    });

    const {value: newPin, errorMessage: newPinError} = useField('newPin');
    const {value: confirmNewPin, errorMessage: confirmNewPinError} = useField('confirmNewPin');


    const patchNewPin = handleNewPinSubmit(() => {
      const userId = setNewPinModalInfo.value.id;
      requests.patchUser(userId, {pinCleartext: newPin.value}).then((response) => {
        const indexInArray = userData.value.findIndex((user) => (user.id === userId));
        userData.value.splice(indexInArray, 1, response.data);
        toast.success('PIN changed!', {timeout: 2000});
      }).finally(() => {
        resetNewPinForm();
        showSetNewPinModal.value = !showSetNewPinModal.value;
      });
    });

    return {
      username,
      usernameError,
      password,
      passwordError,
      confirmPassword,
      confirmPasswordError,
      pin,
      pinError,
      confirmPin,
      confirmPinError,
      admin,
      depositBearer,
      rentalChecker,
      appointmentManager,
      treasurer,
      userData,
      postNewUser,
      setNewPasswordModalInfo,
      newPassword,
      newPasswordError,
      confirmNewPassword,
      confirmNewPasswordError,
      patchNewPassword,
      showSetNewPasswordModal,
      newPin,
      newPinError,
      setNewPinModalInfo,
      showSetNewPinModal,
      confirmNewPin,
      confirmNewPinError,
      patchNewPin,
    };
  },
  data() {
    return {
      loadingUsers: true,
      userMe: {},
      userActions: [],
      userActionsIfAdmin: [
        {
          label: 'Set New Password',
          id: 'newPassword',
          icon: 'heroicons:key',
          func: this.openSetNewPasswordModal,
        },
        {
          label: 'Set New PIN',
          id: 'newPin',
          icon: 'heroicons:finger-print',
          func: this.openSetNewPinModal,
        },
      ],
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
        {
          label: 'Actions',
          field: 'actions',
        },
      ],
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
    openSetNewPasswordModal(userId) {
      this.showSetNewPasswordModal = !this.showSetNewPasswordModal;
      this.setNewPasswordModalInfo = this.userData[this.userData.findIndex((user) => user.id === userId)];
    },
    openSetNewPinModal(userId) {
      this.showSetNewPinModal = !this.showSetNewPinModal;
      this.setNewPinModalInfo = this.userData[this.userData.findIndex((user) => user.id === userId)];
    },
  },
  created() {
    this.getUserData();
    requests.getUserMe().then((response) => {
      this.userMe = response.data;
      if (this.userMe.admin) {
        this.userActions = this.userActionsIfAdmin;
      }
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="2xl:col-span-9 col-span-12">
      <Card title="Users">
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <UserRolesTable :loading="loadingUsers" :actions="userActions" :columns="userColumns" :table-data="userData" :patch-user="patchUser" :userIsAdmin="userMe.admin"></UserRolesTable>
            <SetNewPasswordModal :active-modal="showSetNewPasswordModal" title="Set new password" :user-info="setNewPasswordModalInfo" @close="showSetNewPasswordModal = !showSetNewPasswordModal">
              <div>
                <form @submit.prevent="patchNewPassword" class="space-y-4">
                  <Textinput
                      label="New Password"
                      type="password"
                      placeholder="New Password"
                      name="newPassword"
                      v-model="newPassword"
                      :error="newPasswordError"
                      hasicon
                      classInput="h-[48px]"
                  />
                  <Textinput
                      label="Confirm New Password"
                      type="password"
                      placeholder="Confirm New Password"
                      name="confirmNewPassword"
                      v-model="confirmNewPassword"
                      :error="confirmNewPasswordError"
                      hasicon
                      classInput="h-[48px]"
                  />

                  <Button type="submit" class="btn btn-dark block w-full text-center">
                    Submit
                  </Button>
                </form>
              </div>
            </SetNewPasswordModal>
            <SetNewPasswordModal :active-modal="showSetNewPinModal" :user-info="setNewPinModalInfo" title="Set new PIN" @close="showSetNewPinModal = !showSetNewPinModal">
              <div>
                <form @submit.prevent="patchNewPin" class="space-y-4">
                  <Textinput
                      label="New 4-digit PIN"
                      type="password"
                      placeholder="0000"
                      name="newPin"
                      v-model="newPin"
                      :error="newPinError"
                      hasicon
                      classInput="h-[48px]"
                  />
                  <Textinput
                      label="Confirm PIN"
                      type="password"
                      placeholder="0000"
                      name="confirmNewPin"
                      v-model="confirmNewPin"
                      :error="confirmNewPinError"
                      hasicon
                      classInput="h-[48px]"
                  />

                  <Button type="submit" class="btn btn-dark block w-full text-center">
                    Submit
                  </Button>
                </form>
              </div>
            </SetNewPasswordModal>
          </div>
        </div>
      </Card>
    </div>
    <div class="2xl:col-span-3 col-span-12">
      <Card title="Add User">
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <form @submit.prevent="postNewUser" class="space-y-4">
              <Textinput
                  label="Username"
                  type="username"
                  placeholder="username"
                  name="username"
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
              <Textinput
                  label="Confirm Password"
                  type="password"
                  placeholder="Confirm Password"
                  name="confirmPassword"
                  v-model="confirmPassword"
                  :error="confirmPasswordError"
                  hasicon
                  classInput="h-[48px]"
              />
              <Textinput
                  label="4-digit PIN"
                  type="password"
                  placeholder="0000"
                  name="pin"
                  v-model="pin"
                  :error="pinError"
                  hasicon
                  classInput="h-[48px]"
              />
              <Textinput
                  label="Confirm PIN"
                  type="password"
                  placeholder="0000"
                  name="confirmPin"
                  v-model="confirmPin"
                  :error="confirmPinError"
                  hasicon
                  classInput="h-[48px]"
              />
              <Checkbox
                  label="Admin"
                  name="admin"
                  v-model="admin"/>
              <Checkbox
                  label="Deposit Bearer"
                  name="depositBearer"
                  v-model="depositBearer"/>
              <Checkbox
                  label="Rental Checker"
                  name="rentalChecker"
                  v-model="rentalChecker"/>
              <Checkbox
                  label="Appointment Manager"
                  name="appointmentManager"
                  v-model="appointmentManager"/>
              <Checkbox
                  label="Treasurer"
                  name="treasurer"
                  v-model="treasurer"/>

              <Button type="submit" class="btn btn-dark block w-full text-center">
                Submit
              </Button>
            </form>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>