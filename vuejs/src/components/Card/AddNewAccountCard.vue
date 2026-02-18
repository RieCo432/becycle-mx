<script>
import Card from '@/components/Card/index.vue';
import Checkbox from '@/components/Switch/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import Button from '@/components/Button/index.vue';
import {ref, toRef} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import Select from '@/components/Select/index.vue';
import VueSelect from '@/components/Select/VueSelect.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';

import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'AddNewAccountCard',
  components: {ComboboxTextInput, VueSelect, Select, Button, TextInput, Checkbox, Card},
  setup(props, context) {
    const existingAccounts = toRef(props, 'accounts');
    const users = ref([]);
    const groups = ref([]);

    requests.getUsers().then((response) => {
      response.data.forEach((u) => users.value.push(u));
    });
    requests.getUserGroups().then((response) => {
      response.data.forEach((g) => groups.value.push(g));
    });

    const availableUiFilters = ['deposit', 'expense', 'income', 'transfer', 'return'];
    const accountTypes = ['dividend', 'expense', 'asset', 'liability', 'equity', 'revenue'];

    const newAccountSchema = yup.object().shape({
      name: yup
        .string()
        .required('Name is required')
        .lowercase()
        .notOneOf(existingAccounts.value.map((a) => a.name), 'This name exists already!')
        .max(60, 'No more than 30 characters'),
      description: yup
        .string()
        .required('Description is required')
        .max(255, 'No more than 255 characters'),
      type: yup
        .string()
        .required('Type is required')
        .oneOf(accountTypes, `Type must be one of: ${accountTypes.join(', ')} `),
      ownerUsername: yup.string().nullable(),
      ownerGroupName: yup.string().nullable(),
      scheduledClosureDate: yup.date().nullable(),
      isInternal: yup.bool(),
      showInUis: yup.array().of(yup.object().shape({
        label: yup.string().oneOf(availableUiFilters),
        value: yup.string().oneOf(availableUiFilters),
      })),
    });


    const {handleSubmit: handleNewAccountSubmit, resetForm: resetNewAccountForm} = useForm({
      validationSchema: newAccountSchema,
      keepValuesOnUnmount: true,
    });

    const {value: name, errorMessage: nameError} = useField('name');
    const {value: description, errorMessage: descriptionError} = useField('description');
    const {value: type, errorMessage: typeError} = useField('type');
    const {value: ownerUsername, errorMessage: ownerUsernameError, setErrors: setOwnerUsernameErrors} = useField('ownerUsername');
    const {value: ownerGroupName, errorMessage: ownerGroupNameError, setErrors: setOwnerGroupNameErrors} = useField('ownerGroupName');
    const {value: scheduledClosureDate, errorMessage: scheduledClosureDateError} = useField('scheduledClosureDate');
    const {value: isInternal, errorMessage: isInternalError} = useField('isInternal');
    const {value: showInUis, errorMessage: showInUisError} = useField('showInUis');

    function validateOwnerUsername() {
      if (
        ownerUsername.value &&
        ownerUsername.value !== '' &&
        !users.value.find((u) => u.username === ownerUsername.value)) {
        setOwnerUsernameErrors(['Owner username must be a valid username']);
      }
    }

    function validateOwnerGroupName() {
      if (
        ownerGroupName.value &&
        ownerGroupName.value !== '' &&
        !groups.value.find((g) => g.name === ownerGroupName.value)) {
        setOwnerGroupNameErrors(['Owner group name must be a valid group name']);
      }
    }

    const postNewAccount = handleNewAccountSubmit(() => {
      requests.postNewAccount(
        name.value.toLowerCase(),
        description.value.toLowerCase(),
        type.value.toLowerCase(),
        ownerUsername.value && ownerUsername.value !== '' ?
          users.value.find((u) => u.username === ownerUsername.value).id :
          null,
        ownerGroupName.value && ownerGroupName.value !== '' ?
          groups.value.find((g) => g.name === ownerGroupName.value).id :
          null,
        scheduledClosureDate.value,
        isInternal.value,
        showInUis.value.map((f) => f.value.toLowerCase()))
        .then((response) => {
          toast.success('Account created!', {timeout: 2000});
          context.emit('accountCreated');
        }).finally(() => {
          resetNewAccountForm();
        });
    });

    return {
      accountTypes,
      users,
      groups,
      availableUiFilters,
      name,
      nameError,
      description,
      descriptionError,
      type,
      typeError,
      ownerUsername,
      ownerUsernameError,
      ownerGroupName,
      ownerGroupNameError,
      scheduledClosureDate,
      scheduledClosureDateError,
      isInternal,
      isInternalError,
      showInUis,
      showInUisError,
      postNewAccount,
      validateOwnerUsername,
      validateOwnerGroupName,
    };
  },
  emits: ['accountCreated'],
  props: {
    accounts: {
      type: Array,
      required: true,
    },
  },
  methods: {
    selectOwnerUser(event, i) {
      if (i !== -1) {
        this.ownerUsername = this.filtered_user_suggestions[i];
      }
    },
    selectOwnerGroup(event, i) {
      if (i !== -1) {
        this.ownerGroupName = this.filtered_group_suggestions[i];
      }
    },
    userSortingFunction(user1, user2) {
      if (user1.toLowerCase() > user2.toLowerCase()) return 1;
      if (user1.toLowerCase() < user2.toLowerCase()) return -1;
      return 0;
    },
  },
  computed: {
    filtered_user_suggestions() {
      return this.users.map((u) => u.username)
        .filter((suggestion) => suggestion
          .toLowerCase()
          .startsWith((this.ownerUsername ?? '').toLowerCase()))
        .sort(this.userSortingFunction)
        .slice(0, 10);
    },
    filtered_group_suggestions() {
      return this.groups.map((g) => g.name)
        .filter((suggestion) => suggestion
          .toLowerCase()
          .startsWith((this.ownerGroupName ?? '').toLowerCase()))
        .sort(this.userSortingFunction)
        .slice(0, 10);
    },
  },
};
</script>

<template>
  <Card title="Add User">
    <div class="grid grid-cols-12">
      <div class="col-span-12">
        <form @submit.prevent="postNewAccount" class="space-y-4">
          <TextInput
              label="Name"
              type="text"
              placeholder="Deposit Liability Account"
              name="name"
              v-model="name"
              :error="nameError"
              classInput="h-[48px]"
          />
          <TextInput
              label="Description"
              type="text"
              placeholder="This is the main liability account for all deposits"
              name="description"
              v-model="description"
              :error="descriptionError"
              classInput="h-[48px]"
          />
          <div class="col-span-6">
            <Select
                :options="accountTypes.map((i) => ({value: i, label: i}))"
                label="Type of Account"
                v-model="type"
                name="type"
                :error="typeError"
            />
          </div>

            <ComboboxTextInput
                    :field-model-value="ownerUsername"
                    :suggestions="filtered_user_suggestions"
                    :selected-callback="selectOwnerUser"
                    :allow-new="false"
                    label="Owner User"
                    type="text"
                    placeholder="workshop"
                    name="ownerUsername"
                    v-model="ownerUsername"
                    :error="ownerUsernameError"
                    @change="() => {validateOwnerUsername()}"
            />

            <ComboboxTextInput
                    :field-model-value="ownerGroupName"
                    :suggestions="filtered_group_suggestions"
                    :selected-callback="selectOwnerGroup"
                    :allow-new="false"
                    label="Owner Group"
                    type="text"
                    placeholder="volunteers"
                    name="ownerGroupName"
                    v-model="ownerGroupName"
                    :error="ownerGroupNameError"
                    @change="() => {validateOwnerGroupName()}"
            />

          <div class="col-span-6 content-center">
            <label class="text-slate-700 dark:text-slate-300">Scheduled Closure Date</label>
            <flat-pickr
                class="form-control m-auto"
                name="scheduledClosureDate"
                id="d3"
                placeholder="dd-mm-yyyy"
                v-model="scheduledClosureDate"
                :config="{ enableTime: false, dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y'}"
            >
            </flat-pickr>
            <ErrorMessage name="scheduledClosureDate" :error="scheduledClosureDateError" class="text-danger-500"/>
          </div>

          <Checkbox
              label="Internal Account?"
              name="isInternal"
              v-model="isInternal"/>

          <div class="col-span-12">
            <VueSelect
                label="Show in UIs"
                name="showInUis"
                :options="availableUiFilters.map((i) => ({value: i, label: i}))"
                v-model="showInUis"
                :error="showInUisError"
                multiple
            />
          </div>

          <Button type="submit" class="btn btn-dark block w-full text-center">
            Submit
          </Button>
        </form>
      </div>
    </div>
  </Card>

</template>

<style scoped lang="scss">

</style>
