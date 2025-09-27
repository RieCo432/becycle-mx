<script>
import Modal from '@/components/Modal/Modal.vue';
import Button from '@/components/Button/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import {toRef} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import ComboboxColourPicker from '@/components/ComboBoxColourPicker/ComboboxColourPicker.vue';

const toast = useToast();

export default {
  name: 'EditBikeDetailsModal',
  components: {ComboboxColourPicker, TextInput, Button, Modal},
  setup(props, context) {
    const closeModal = toRef(props, 'closeModal');
    const bike = toRef(props, 'bike');
    const newDetailsSchema = yup.object().shape({
      make: yup.string().required('Make is required'),
      model: yup.string().required('Modal is required'),
      colours: yup.array().required('Colour is required').max(3, 'Maximum of 3 colours.').min(1, 'Minimum of 1 colour.'),
      decals: yup.string().nullable(),
      serialNumber: yup.string().required('Serial Number is required'),
    });

    const {handleSubmit} = useForm({
      validationSchema: newDetailsSchema,
      keepValuesOnUnmount: true,
    });

    const {value: make, errorMessage: makeError} = useField('make');
    const {value: model, errorMessage: modelError} = useField('model');
    const {value: colours, errorMessage: coloursError} = useField('colours');
    const {value: decals, errorMessage: decalsError} = useField('decals');
    const {value: serialNumber, errorMessage: serialNumberError} = useField('serialNumber');

    const submitChangeDetails = handleSubmit(() => {
      requests.patchBikeChangeDetails(bike.value.id, {
        make: make.value,
        model: model.value,
        colours: colours.value,
        decals: decals.value,
        serialNumber: serialNumber.value,
      }).then((response) => {
        toast.success('Bike Details updated', {timeout: 2000});
        context.emit('bikeDetailsUpdated', response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      }).finally(() => {
        closeModal.value();
      });
    });

    return {
      make,
      makeError,
      model,
      modelError,
      colours,
      coloursError,
      decals,
      decalsError,
      serialNumber,
      serialNumberError,
      submitChangeDetails,
    };
  },
  emits: [
    'bikeDetailsUpdated',
  ],
  props: {
    bike: {
      type: Object,
      required: true,
    },
    showModal: {
      type: Boolean,
      required: true,
    },
    closeModal: {
      type: Function,
      required: true,
    },
  },
  mounted() {
    this.make = this.bike.make;
    this.model = this.bike.model;
    this.colours = this.bike.colours;
    this.colour = this.bike.colours;
    this.decals = this.bike.decals;
    this.serialNumber = this.bike.serialNumber;
  },
};
</script>

<template>
  <Modal :active-modal="showModal" @close="closeModal" title="Edit Details">
    <form @submit.prevent="submitChangeDetails">
      <div class="grid grid-cols-12 gap-5">
        <div class="md:col-span-6 col-span-12">
          <TextInput
              label="Make"
              type="text"
              placeholder="raleigh"
              name="make"
              v-model="make"
              :error="makeError"
          />
        </div>
        <div class="md:col-span-6 col-span-12">
          <TextInput
              label="Model"
              type="text"
              placeholder="chloe"
              name="model"
              v-model="model"
              :error="modelError"
          />
        </div>
        <div class="col-span-12">
          <ComboboxColourPicker
              :suggestions="[]"
              :selected-callback="() => {}"
              :allow-new=false
              :error="coloursError"
              label="Colours"
              name="colours"
              @update:modelValue="(newValue) => {colours = newValue}"
              v-model="colours"
              @click.prevent="() => {}"
          />
        </div>
        <div class="col-span-12">
          <TextInput
              label="Decals"
              type="text"
              placeholder="some stickers"
              name="decals"
              v-model="decals"
              :error="decalsError"
          />
        </div>
        <div class="col-span-full">
          <TextInput
              label="Serial Number"
              type="text"
              placeholder="abcd 1234"
              name="serialNumber"
              v-model="serialNumber"
              :error="serialNumberError"
          />
        </div>
        <div class="col-span-12">
          <Button type="submit" class="btn btn-dark block w-full text-center">
            Submit
          </Button>
        </div>
      </div>
    </form>
  </Modal>
</template>

<style scoped lang="scss">

</style>
