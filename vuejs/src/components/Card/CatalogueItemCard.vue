<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {ref, toRef} from 'vue';
import DashButton from '@/components/Button/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import {useDropzone} from 'vue3-dropzone';
import {Icon} from '@iconify/vue';
import Button from '@/components/Button/index.vue';
import {useToast} from 'vue-toastification';
import Switch from '@/components/Switch';

const toast = useToast();


export default {
  name: 'CatalogueItemCard',
  components: {Button, Icon, TextInput, DashButton, Card, Switch},
  props: {
    presentationCardDetails: {
      type: Object,
      required: true,
    },
    editable: {
      type: Boolean,
    },
    updateItemDetails: {
      type: Function,
      required: false,
    },
  },
  methods: {
    openEditMode() {
      this.inEditMode = true;
      this.name = this.presentationCardDetails.name;
      this.description = this.presentationCardDetails.description;
    },
    toggleAvailability() {
      requests.patchCatalogueItemAvailability(this.presentationCardDetails.id, !this.presentationCardDetails.available).then((response) => {
        toast.success('Catalogue item availability updated successfully', {timeout: 2000});
        this.$emit('catalogueItemUpdated', response.data);
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
  },
  created() {
    this.getImage();
  },
  emits: ['catalogueItemUpdated'],
  setup(props, context) {
    const inEditMode = ref(false);
    const isOldPhoto = ref(true);
    const photoUrl = ref(null);
    const itemDetails = toRef(props, 'itemDetails');
    const editItemSchema = yup.object().shape({
      name: yup.string().max(60).required('Name is required'),
      description: yup.string().max(512).required('Description is required'),
      isSecondHand: yup.boolean().required('Is second hand is required'),
    });

    function getImage() {
      if (itemDetails.value.catalogueItemPhotoId) {
        requests.getCatalogueItemPhoto(itemDetails.value.id).then((response) => {
          const photoFile = new File([response.data], itemDetails.value.catalogueItemPhotoId, {type: response.data.type});
          photoUrl.value = window.URL.createObjectURL(photoFile);
          files.value.splice(0, files.value.length, Object.assign(photoFile, {preview: photoUrl.value}));
        });
      }
    }

    const {handleSubmit} = useForm({
      validationSchema: editItemSchema,
      keepValuesOnUnmount: true,
    });

    const {value: name, errorMessage: nameError} = useField('name');
    const {value: description, errorMessage: descriptionError} = useField('description');
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
      requests.putUpdateCatalogueItem(
        itemDetails.value.id,
        name.value,
        description.value,
        isSecondHand.value,
        !isOldPhoto.value ? files.value[0] : undefined)
        .then((response) => {
          toast.success('Catalogue item updated successfully', {timeout: 2000});
          context.emit('catalogueItemUpdated', response.data);
          if (!isOldPhoto.value) getImage();
          inEditMode.value = false;
          isOldPhoto.value = true;
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    });

    return {
      getRootProps,
      getInputProps,
      ...rest,
      files,
      inEditMode,
      name,
      nameError,
      description,
      descriptionError,
      isSecondHand,
      isSecondHandError,
      submitItemDetails,
      isOldPhoto,
      getImage,
      photoUrl,
    };
  },
};
</script>

<template>
  <Card
    class-name="rounded-3xl border border-solid dark:border-slate-600 border-l-2 border-t-2 shadow-lg dark:shadow-slate-900 h-full"
    body-class="p-0">
    <div v-if="!inEditMode" class="h-full w-full flex flex-col ">
      
      <div class="grid grid-cols-4 md:grid-cols-3 lg:grid-cols-1 flex-shrink">
        <div class="col-span-1 row-span-5 lg:row-span-1">
          <img v-if="!inEditMode && photoUrl" :src="photoUrl" alt="Item Picture" class="aspect-square rounded-3xl h-full w-full"/>
          <img v-if="!inEditMode && !photoUrl" src="@/assets/images/defaultProfilePicture.jpg"
               alt="Item Picture" class="h-full w-full aspect-square rounded-3xl"/>
        </div>
        <div class="col-span-3 md:col-span-2 lg:col-span-1 p-2">
          <p class="w-full col-span-8 text-slate-700 dark:text-slate-300 text-2xl font-semibold">
            {{ itemDetails.name }}
          </p>
        </div>
        <div class="col-span-3 md:col-span-2 lg:col-span-1 p-2">
          <p class="dark:text-slate-300 text-slate-700 inline-block">{{ itemDetails.description }}</p>
        </div>
        <div class="col-span-3 md:col-span-2 lg:col-span-1 p-2 dark:text-slate-300 text-slate-700 flex justify-between" v-if="!inEditMode">
          <div>Purchase Price:</div>
          <div>&#163; {{ (itemDetails.purchasePrice / 100).toFixed(2) }}</div>
        </div>
        <div class="col-span-3 md:col-span-2 lg:col-span-1 p-2 flex-row dark:text-slate-300 text-slate-700 flex justify-between" v-if="!inEditMode">
          <div>Recommended Price:</div>
          <div>&#163; {{ (itemDetails.recommendedRetailPrice / 100).toFixed(2) }}</div>
        </div>
        <div class="col-span-3 md:col-span-2 lg:col-span-1 p-2 flex-row dark:text-slate-300 text-slate-700 flex justify-between" v-if="!inEditMode">
          <div>Condition:</div>
          <div>{{ itemDetails.isSecondHand ? 'Used' : 'New' }}</div>
        </div>
      </div>

      <div v-if="editable" class="grid grid-cols-2 w-full mt-auto bottom-0">
        <Button @click.prevent="openEditMode" class="col-span-1 rounded-l-full">
          <Icon icon="heroicons-outline:pencil"></Icon>
        </Button>
        <Button
          @click.prevent="toggleAvailability"
          class="col-span-1 rounded-r-full"
          :btn-class="itemDetails.available
            ? 'btn-success'
            : 'btn-danger'">
          <Icon icon="heroicons-outline:check-circle" v-if="itemDetails.available"></Icon>
          <Icon icon="heroicons-outline:no-symbol" v-else></Icon>
        </Button>
      </div>
    </div>
    
    <form v-else @submit.prevent="submitItemDetails">
      <div class="grid grid-cols-2">
        <div class="col-span-2">
          <div class="h-full w-full aspect-square" @click="() => {
            files = [];
            isOldPhoto = false;
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
                   alt="Item Picture"
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
              placeholder="Spare derailleurs from the box"
              name="description"
              v-model="description"
              :error="descriptionError"
          />
        </div>
        <div class="col-span-2 p-2">
          <Switch
            label="Is second hand?"
            name="isSecondHand"
            v-model="isSecondHand"
          />
        </div>
        <div class="col-span-2 p-3" v-if="inEditMode">
          <div class="grid grid-cols-2">
            <DashButton v-if="inEditMode" @click="submitItemDetails" class="col-span-2 justify-self-end my-auto rounded-full">
              Update
            </DashButton>
          </div>
        </div>
      </div>
    </form>
  </Card>
</template>

<style scoped lang="scss">

</style>
