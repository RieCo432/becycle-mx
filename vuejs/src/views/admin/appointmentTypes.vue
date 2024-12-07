<script>
import Card from '@/components/Card/index.vue';
import {ref} from 'vue';
import AppointmentTypesTable from '@/components/Tables/AppointmentTypesTable.vue';
import requests from '@/requests';
import Modal from '@/components/Modal/Modal.vue';
import {useToast} from 'vue-toastification';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import Textinput from '@/components/Textinput/index.vue';
import Select from '@/components/Select/index.vue';
import Checkbox from '@/components/Switch/index.vue';
import Button from '@/components/Button/index.vue';
import CreateNewAppointmentTypeCard from '@/components/Card/CreateNewAppointmentTypeCard.vue';

const toast = useToast();

export default {
  name: 'appointmentTypes',
  components: {
    CreateNewAppointmentTypeCard,
    Button,
    Checkbox,
    Select,
    Textinput,
    AppointmentTypesTable,
    Card,
    Modal,
  },
  setup() {
    const appointmentTypes = ref([]);
    const editAppointmentTypeModalInfo = ref({});
    const showEditAppointmentTypeModal = ref(false);

    const editAppointmentTypeSchema = yup.object().shape({
      editAppointmentTypeTitle: yup.string().max(30).required('Appointment Type Title is required'),
      editAppointmentTypeDescription: yup.string().max(300).required('Appointment Type description is required'),
      editAppointmentTypeDuration: yup.number().integer('Duration must be an integer number of minutes').positive('Duration must be a positive number of minutes').required('Duration is required'),
      editAppointmentTypeActive: yup.bool(),
    });

    const {handleSubmit: handleEditAppointmentTypeSubmit, resetForm: resetEditAppointmentTypeForm} = useForm({
      validationSchema: editAppointmentTypeSchema,
      keepValuesOnUnmount: true,
    });

    const {value: editAppointmentTypeTitle, errorMessage: editAppointmentTypeTitleError, resetField: resetEditAppointmentTypeTitleField} = useField('editAppointmentTypeTitle');
    const {value: editAppointmentTypeDescription, errorMessage: editAppointmentTypeDescriptionError, resetField: resetEditAppointmentTypeDescriptionField} = useField('editAppointmentTypeDescription');
    const {value: editAppointmentTypeDuration, errorMessage: editAppointmentTypeDurationError, resetField: resetEditAppointmentTypeDurationField} = useField('editAppointmentTypeDuration');
    const {value: editAppointmentTypeActive, resetField: resetEditAppointmentTypeActiveField} = useField('editAppointmentTypeActive');

    const patchEditAppointmentTypeSubmit = handleEditAppointmentTypeSubmit(() => {
      requests.patchAppointmentType(editAppointmentTypeModalInfo.value.id, {
        title: editAppointmentTypeTitle.value,
        description: editAppointmentTypeDescription.value,
        duration: editAppointmentTypeDuration.value,
        active: editAppointmentTypeActive.value,
      }).then((response) => {
        const indexInArray = appointmentTypes.value.findIndex((appointmentType) => (appointmentType.id === editAppointmentTypeModalInfo.value.id));
        appointmentTypes.value.splice(indexInArray, 1, response.data);
        toast.success('Appointment Type updated', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      }).finally(() => {
        resetEditAppointmentTypeForm();
        showEditAppointmentTypeModal.value = !showEditAppointmentTypeModal.value;
      });
    });

    return {
      showEditAppointmentTypeModal,
      appointmentTypes,
      editAppointmentTypeModalInfo,
      editAppointmentTypeTitle,
      editAppointmentTypeTitleError,
      resetEditAppointmentTypeTitleField,
      editAppointmentTypeDescription,
      editAppointmentTypeDescriptionError,
      resetEditAppointmentTypeDescriptionField,
      editAppointmentTypeDuration,
      editAppointmentTypeDurationError,
      resetEditAppointmentTypeDurationField,
      editAppointmentTypeActive,
      resetEditAppointmentTypeActiveField,
      patchEditAppointmentTypeSubmit,
    };
  },
  methods: {
    openEditAppointmentTypeModal(appointmentTypeId) {
      this.showEditAppointmentTypeModal = !this.showEditAppointmentTypeModal;
      this.editAppointmentTypeModalInfo = this.appointmentTypes[this.appointmentTypes.findIndex((appointmentType) => (appointmentType.id === appointmentTypeId))];
      this.resetEditAppointmentTypeTitleField(
          {
            value: this.editAppointmentTypeModalInfo.title,
          },
      );
      this.resetEditAppointmentTypeDescriptionField(
          {
            value: this.editAppointmentTypeModalInfo.description,
          },
      );
      this.resetEditAppointmentTypeDurationField(
          {
            value: this.editAppointmentTypeModalInfo.duration.toString(),
          },
      );
      this.resetEditAppointmentTypeActiveField(
          {
            value: this.editAppointmentTypeModalInfo.active,
          },
      );
    },
    patchAppointmentType(appointmentTypeId, patchData, failureCallback) {
      requests.patchAppointmentType(appointmentTypeId, patchData)
          .then((response) => {
            const indexInArray = this.appointmentTypes.findIndex((appointmentType) => (appointmentType.id === appointmentTypeId));
            this.appointmentTypes.splice(indexInArray, 1, response.data);
            toast.success('Appointment Type updated', {timeout: 2000});
          })
          .catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 2000});
            failureCallback();
          });
    },
  },
  data() {
    return {
      loadingAppointmentTypes: true,
      appointmentTypesActions: [
        {
          label: 'Edit',
          icon: 'heroicons-outline:pencil-square',
          func: this.openEditAppointmentTypeModal,
        },
      ],
      appointmentTypesColumns: [
        {
          label: 'ID',
          field: 'id',
        },
        {
          label: 'Active',
          field: 'active',
        },
        {
          label: 'Title',
          field: 'title',
        },
        {
          label: 'Description',
          field: 'description',
        },
        {
          label: 'Duration (minutes)',
          field: 'duration',
        },
        {
          label: 'Actions',
          field: 'actions',
        },
      ],
    };
  },
  created() {
    requests.getAppointmentTypes(true).then((response) => {
      this.appointmentTypes = response.data;
      this.loadingAppointmentTypes = false;
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="2xl:col-span-9 col-span-12">
      <Card title="Appointment Types">
        <div class="grid grid-cols-12">
          <div class="col-span-12">
            <AppointmentTypesTable
                :loading="loadingAppointmentTypes"
                :actions="appointmentTypesActions"
                :columns="appointmentTypesColumns"
                :table-data="appointmentTypes"
                :patch-appointment-type="patchAppointmentType"
            ></AppointmentTypesTable>
            <Modal :title="`Edit Appointment Type ${editAppointmentTypeModalInfo.id}`" :active-modal="showEditAppointmentTypeModal" @close="showEditAppointmentTypeModal = !showEditAppointmentTypeModal">
              <div class="grid grid-cols-12">
                <div class="col-span-12">
                  <form @submit.prevent="patchEditAppointmentTypeSubmit" class="space-y-4">
                    <Textinput
                        label="Appointment Type Title"
                        type="text"
                        placeholder="Small Repair"
                        name="editAppointmentTypeTitle"
                        v-model="editAppointmentTypeTitle"
                        :error="editAppointmentTypeTitleError"
                    />
                    <Textinput
                        label="Appointment Type Description"
                        type="text"
                        placeholder="Fix something small, like tighten brakes"
                        name="editAppointmentTypeDescription"
                        v-model="editAppointmentTypeDescription"
                        :error="editAppointmentTypeDescriptionError"
                    />
                    <Textinput
                        label="Appointment Type Duration"
                        type="text"
                        placeholder="15"
                        name="editAppointmentTypeDuration"
                        v-model="editAppointmentTypeDuration"
                        :error="editAppointmentTypeDurationError"
                    />
                    <Checkbox
                        label="Make Available?"
                        name="editAppointmentTypeActive"
                        v-model="editAppointmentTypeActive"
                    />
                    <Button type="submit" class="btn btn-dark block w-full text-center">
                      Submit
                    </Button>
                  </form>
                </div>
              </div>
            </Modal>
          </div>
        </div>
      </Card>
    </div>
    <div class="2xl:col-span-3 col-span-12">
      <CreateNewAppointmentTypeCard @new-appointment-type-created="(newAppointmentType) => appointmentTypes.push(newAppointmentType)"></CreateNewAppointmentTypeCard>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
