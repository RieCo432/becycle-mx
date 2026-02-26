<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {ref} from 'vue';
import TextInput from '@/components/TextInput/index.vue';
import {useDropzone} from 'vue3-dropzone';
import Button from '@/components/Button/index.vue';
import {useToast} from 'vue-toastification';
import Switch from '@/components/Switch';

const toast = useToast();

export default {
  name: 'AddNewCatalogueItemCard',
  components: {Button, TextInput, Card, Switch},
  emits: ['catalogueItemAdded'],

  setup(props, context) {
    const addNewItemSchema = yup.object().shape({
      name: yup
        .string()
        .max(60)
        .required('Name is required'),
      description: yup
        .string()
        .max(512)
        .required('Description is required'),
      purchasePrice: yup
        .number()
        .min(0)
        .nullable()
        .transform((value) => Number.isNaN(value) ? null : value ),
      recommendedRetailPrice: yup
        .number()
        .min(0)
        .nullable()
        .transform((value) => Number.isNaN(value) ? null : value ),
      isSecondHand: yup
        .boolean()
        .required('Is second hand status is required')
        .default(false),
    });

    const {handleSubmit, handleReset: resetNewItemForm} = useForm({
      validationSchema: addNewItemSchema,
      keepValuesOnUnmount: true,
    });

    const {value: name, errorMessage: nameError} = useField('name');
    const {value: description, errorMessage: descriptionError} = useField('description');
    const {value: purchasePrice, errorMessage: purchasePriceError} = useField('purchasePrice');
    const {value: recommendedRetailPrice, errorMessage: recommendedRetailPriceError} = useField('recommendedRetailPrice');
    const {value: isSecondHand, errorMessage: isSecondHandError} = useField('isSecondHand');

    const files = ref([]);
    function onDrop(acceptFiles) {
      files.value = acceptFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
        }),
      );
    }

    const {getRootProps, getInputProps, ...rest} = useDropzone({onDrop, multiple: false});

    const submitItemDetails = handleSubmit(() => {
      console.log(purchasePrice.value, recommendedRetailPrice.value);
      requests.postNewCatalogueItem(
        name.value,
        description.value,
        purchasePrice.value ? purchasePrice.value * 100 : null,
        recommendedRetailPrice.value ? recommendedRetailPrice.value * 100 : null,
        isSecondHand.value,
        files.value[0]).then((response) => {
        toast.success('Item added successfully', {timeout: 2000});
        context.emit('catalogueItemAdded', response.data);
        resetNewItemForm();
        files.value = [];
      });
    });

    return {
      getRootProps,
      getInputProps,
      ...rest,
      files,
      name,
      nameError,
      description,
      descriptionError,
      purchasePrice,
      purchasePriceError,
      recommendedRetailPrice,
      recommendedRetailPriceError,
      isSecondHand,
      isSecondHandError,
      submitItemDetails,
      resetNewItemForm,
    };
  },
};
</script>

<template>
  <Card gap-null class-name="rounded-3xl" body-class="p-0">
    <form @submit.prevent="submitItemDetails">
      <div class="grid grid-cols-2">
        <div class="col-span-2">
          <div class="h-full w-full aspect-square" @click="() => {
            files = [];
          }">
            <div
                v-bind="getRootProps()"
                class="h-full text-center border-dashed border border-secondary-500
                       rounded-3xl flex flex-col justify-center justify-items-center"
                :class="files.length === 0 ? 'cursor-pointer' : ' pointer-events-none'"
            >
              <div v-if="files.length === 0" class="h-full flex items-center">
                <div class="m-auto">
                  <input v-bind="getInputProps()" class="hidden" />
                  <img src="@/assets/images/svg/upload.svg" alt="" class="m-auto"/>
                  <p
                      v-if="isDragActive"
                      class="text-sm text-slate-500 dark:text-slate-300 font-light"
                  >
                    Drop the files here ...
                  </p>
                  <p v-else class="text-sm text-slate-500 dark:text-slate-300 font-light">
                    Drop files here or click to upload.
                  </p>
                </div>
              </div>
              <img v-else
                  :src="files[0].preview"
                  class="object-cover h-full w-full block rounded-3xl aspect-square"
                   alt="Volunteer Presentation Photo"
              />
            </div>
          </div>
        </div>
        <div class="col-span-2 p-2">
          <TextInput
              class="col-span-6"
              label="Name"
              type="text"
              placeholder="Derailleur"
              name="name"
              v-model="name"
              :error="nameError"
          />
        </div>
        <div class="col-span-2 p-2">
          <TextInput
              label="Description"
              type="text"
              placeholder="Spare deraillieurs from the box"
              name="description"
              v-model="description"
              :error="descriptionError"
          />
        </div>
        <div class="col-span-2 p-2">
          <TextInput
              label="Purchase Price (£)"
              type="text"
              placeholder="3.50"
              name="purchasePrice"
              v-model="purchasePrice"
              :error="purchasePriceError"
          />
        </div>
        <div class="col-span-2 p-2">
          <TextInput
              label="Recommended Retail Price (£)"
              type="text"
              placeholder="5.00"
              name="recommendedRetailPrice"
              v-model="recommendedRetailPrice"
              :error="recommendedRetailPriceError"
          />
        </div>
        <div class="col-span-2 p-2">
          <Switch
              label="Is second hand?"
              name="isSecondHand"
              v-model="isSecondHand"
          />
        </div>
        <div class="col-span-1 p-2">
          <Button
              @click.prevent="() => {resetNewItemForm(); files = []}"
              btn-class="btn btn-danger rounded-full block w-full text-center">
            Reset Form
          </Button>
        </div>
        <div class="col-span-1 p-2">
          <Button
              type="submit"
              btn-class="btn btn-primary block w-full text-center rounded-full">
            Submit
          </Button>
        </div>
      </div>
    </form>
  </Card>
</template>

<style scoped lang="scss">

</style>
