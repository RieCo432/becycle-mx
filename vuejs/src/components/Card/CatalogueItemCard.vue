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
import {events as context} from 'vuedraggable/src/core/sortableEvents';

const toast = useToast();


export default {
  name: 'CatalogueItemCard',
  components: {Button, Icon, TextInput, DashButton, Card},
  data() {
    return {
      photoUrl: null,
    };
  },
  props: {
    itemDetails: {
      type: Object,
      required: true,
    },
    editable: {
      type: Boolean,
      required: true,
    },
    updateItemDetails: {
      type: Function,
      required: false,
    },
  },
  methods: {
    openEditMode() {
      this.inEditMode = true;
      this.name = this.itemDetails.name;
      this.description = this.itemDetails.description;
    },
    getImage() {
      console.log('item details', this.itemDetails);
      if (this.itemDetails.catalogueItemPhotoId) {
        requests.getCatalogueItemPhoto(this.itemDetails.id).then((response) => {
          console.log('response', response);
          const photoFile = new File([response.data], this.itemDetails.catalogueItemPhotoId, {type: response.data.type});
          console.log('photoFile', photoFile);
          this.photoUrl = window.URL.createObjectURL(photoFile);
          this.files.splice(0, this.files.length, Object.assign(photoFile, {preview: this.photoUrl}));
        });
      }
    },
  },
  mounted() {
    this.getImage();
  },
  emits: ['catalogueItemUpdated'],
  watch: {
    itemDetails() {
      this.getImage();
    },
  },
  setup(props, context) {
    const inEditMode = ref(false);
    const isOldPhoto = ref(true);
    const itemDetails = toRef(props, 'itemDetails');
    const editItemSchema = yup.object().shape({
      name: yup.string().max(60).required('Name is required'),
      description: yup.string().max(512).required('Description is required'),
    });

    const {handleSubmit} = useForm({
      validationSchema: editItemSchema,
      keepValuesOnUnmount: true,
    });

    const {value: name, errorMessage: nameError} = useField('name');
    const {value: description, errorMessage: descriptionError} = useField('description');

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
        !isOldPhoto.value ? files.value[0] : undefined)
        .then((response) => {
          toast.success('Catalogue item updated successfully', {timeout: 2000}),
          context.emit('catalogueItemUpdated', response.data);
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
      submitItemDetails,
      isOldPhoto,
    };
  },
};
</script>

<template>
  <Card gap-null class-name="rounded-3xl" body-class="p-0">
    <form @submit.prevent="submitItemDetails">
      <div class="grid grid-cols-5 md:grid-cols-9 lg:grid-cols-12">
        <div class="col-span-5">
          <img v-if="!inEditMode && photoUrl" :src="photoUrl" alt="Item Picture" class="aspect-square rounded-3xl"/>
          <img v-if="!inEditMode && !photoUrl" src="@/assets/images/defaultProfilePicture.jpg"
               alt="Item Picture" class="aspect-square rounded-3xl"/>
          <div v-if="inEditMode" class="h-full w-full aspect-square" @click="() => {
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
        <div class="col-span-5 md:col-span-4 lg:col-span-7">
          <div class="grid grid-cols-1 divide-y divide-solid divide-slate-600">
            <div class="col-span-1 p-3">
              <div class="grid grid-cols-8" v-if="!inEditMode">
                <p class="w-full col-span-6 text-slate-700 dark:text-slate-300 text-2xl truncate font-semibold">
                  {{ itemDetails.name }}
                </p>
                <Button v-if="editable" @click="openEditMode" class="col-span-1 rounded-l-full">
                  Edit
                </Button>
              </div>
              <div class="grid grid-cols-8" v-if="inEditMode">
                <TextInput
                    class="col-span-6"
                    v-if="inEditMode"
                    label="Name"
                    type="text"
                    placeholder="Derailleur"
                    name="name"
                    v-model="name"
                    :error="nameError"
                />
                <DashButton v-if="inEditMode" @click="submitItemDetails" class="col-span-2 justify-self-end my-auto rounded-full">
                  <Icon icon="heroicons-outline:check"></Icon>
                </DashButton>
              </div>
            </div>
            <div class="col-span-1 p-3">
              <p v-if="!inEditMode" class="dark:text-slate-300 text-slate-700 inline-block">{{ itemDetails.description }}</p>
              <TextInput
                  v-if="inEditMode"
                  label="Description"
                  type="text"
                  placeholder="Spare derailleurs from the box"
                  name="description"
                  v-model="description"
                  :error="descriptionError"
              />
            </div>
          </div>
        </div>
      </div>
    </form>
  </Card>
</template>

<style scoped lang="scss">

</style>
