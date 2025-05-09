<script>
import TextInput from '@/components/TextInput/index.vue';
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import requests from '@/requests';
import {ref} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'ManageContractTypesCard',
  components: {DashButton, Card, TextInput},
  props: {
    user: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const contractTypes = ref([]);

    const newContractTypeSchema = yup.object().shape({
      newContractTypeId: yup.string().max(20).required(),
    });

    const {handleSubmit: handleNewContractTypeSubmit} = useForm({
      validationSchema: newContractTypeSchema,
      keepValuesOnDismount: true,
    });

    const {value: newContractTypeId, errorMessage: newContractTypeIdError,
      resetField: resetNewContractTypeId} = useField('newContractTypeId');

    const submitNewContractType = handleNewContractTypeSubmit(() => {
      requests.postContractType(newContractTypeId.value).then((response) => {
        console.log(response);
        contractTypes.value.push(response.data);
        resetNewContractTypeId();
        toast.success('Contract Type created', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      contractTypes,
      newContractTypeId,
      newContractTypeIdError,
      submitNewContractType,
    };
  },
  methods: {
    deleteContractType(contractTypeId) {
      requests.deleteContractType(contractTypeId)
        .then((response) => {
          const indexInArray = this.contractTypes.findIndex((t) => (t.id === response.data.id));
          this.contractTypes.splice(indexInArray, 1);
          toast.success('Contract Type deleted', {timeout: 2000});
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    },
  },
  mounted() {
    requests.getContractTypes().then((response) => {
      this.contractTypes = response.data;
    });
  },
};
</script>

<template>
  <Card title="Manage Contract Types">
      <div class="grid grid-cols-12 gap-2">
        <div class="col-span-10">
          <span class="text-slate-700 dark:text-slate-300 text-xl">Contract Type</span>
        </div>
        <div class="col-span-2">
          <span class="text-slate-700 dark:text-slate-300 text-xl">Action</span>
        </div>
        <template v-for="contractType in contractTypes" :key="contractType.id">
          <div class="col-span-10">
            <span class="text-slate-700 dark:text-slate-300">{{contractType.id}}</span>
          </div>
          <div class="col-span-2">
            <DashButton
                v-if="user.admin"
                @click="deleteContractType(contractType.id)"
                class="bg-danger-500 dark:bg-danger-600 btn-sm mx-auto block-btn"
                icon="heroicons-outline:trash"/>
          </div>
        </template>
      </div>
    <form v-if="user.admin" @submit.prevent="submitNewContractType">
      <div class="grid grid-cols-12 gap-2 mt-2">
          <div class="col-span-10">
            <TextInput
                type="text"
                placeholder="New Contract Type"
                name="newContractType"
                v-model="newContractTypeId"
                :error="newContractTypeIdError"
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
