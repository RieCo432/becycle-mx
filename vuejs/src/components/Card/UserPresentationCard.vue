<script>
import Card from '@/components/Card/index.vue';
import requests from '@/requests';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {ref, toRef, watch} from 'vue';
import DashButton from '@/components/Button/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import {useDropzone} from 'vue3-dropzone';
import {Icon} from '@iconify/vue';

const COMMON_NAME = import.meta.env.VITE_COMMON_NAME;

export default {
  name: 'UserPresentationCard',
  components: {Icon, TextInput, DashButton, Card},
  data() {
    return {
      COMMON_NAME: COMMON_NAME,
    };
  },
  props: {
    presentationCardDetails: {
      type: Object,
      required: false,
    },
    editable: {
      type: Boolean,
      required: false,
    },
    updateItemDetails: {
      type: Function,
      required: false,
    },
    deleteCard: {
      type: Function,
      required: false,
    },
    loading: {
      type: Boolean,
      required: false,
      default: false,
    },
    photoUrl: {
      type: String,
      required: false,
    },
  },
  methods: {
    openEditMode() {
      this.inEditMode = true;
      this.name = this.presentationCardDetails.name;
      this.bio = this.presentationCardDetails.bio;
    },
  },
  setup(props, {emit}) {
    const inEditMode = ref(false);
    const isOldPhoto = ref(true);
    const updateItemDetails = toRef(props, 'updateItemDetails');
    const editCardSchema = yup.object().shape({
      name: yup.string().max(20).required('Name is required'),
      bio: yup.string().max(450).required('Bio is required'),
    });

    const {handleSubmit} = useForm({
      validationSchema: editCardSchema,
      keepValuesOnUnmount: true,
    });

    const {value: name, errorMessage: nameError} = useField('name');
    const {value: bio, errorMessage: bioError} = useField('bio');

    const files = ref([]);
    function onDrop(acceptFiles) {
      files.value = acceptFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
        }),
      );
    }

    const {getRootProps, getInputProps, ...rest} = useDropzone({onDrop, multiple: false});

    const submitCardDetails = handleSubmit(() => {
      updateItemDetails.value(name.value, bio.value, !isOldPhoto.value ? files.value[0] : undefined);
      inEditMode.value = false;
      isOldPhoto.value = true;
    });

    watch(() => props.photoUrl, (newValue) => {
      if (!!newValue) {
        files.value.splice(0, files.value.length, {
          preview: props.photoUrl,
        });
      } else {
        files.value.splice(0, files.value.length);
      }
    });

    return {
      getRootProps,
      getInputProps,
      ...rest,
      files,
      inEditMode,
      name,
      nameError,
      bio,
      bioError,
      submitCardDetails,
      isOldPhoto,
    };
  },
};
</script>

<template>
  <Card
    gap-null
    class-name="rounded-3xl"
    body-class="p-0"
  >
    <form @submit.prevent="submitCardDetails">
      <div class="grid grid-cols-5 md:grid-cols-9 lg:grid-cols-12">
        <div class="col-span-5">
          <template v-if="loading">
            <div class="aspect-square rounded-3xl bg-[#C4C4C4] dark:bg-slate-500 animate-pulse"></div>
          </template>
          <template v-else>
            <img v-if="!inEditMode && photoUrl" :src="photoUrl" alt="Profile Picture" class="aspect-square rounded-3xl"/>
            <img v-if="!inEditMode && !photoUrl" src="@/assets/images/defaultProfilePicture.jpg"
                 alt="Profile Picture" class="aspect-square rounded-3xl"/>
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
                     alt="Volunteer Presentation Photo"
                />
              </div>
            </div>
          </template>
        </div>
        <div class="col-span-5 md:col-span-4 lg:col-span-7">
          <div class="grid grid-cols-1 divide-y divide-solid divide-slate-600">
            <div class="col-span-1 p-3">
              <template v-if="loading">
                <p class="w-full col-span-6 text-slate-700 dark:text-slate-300 text-2xl truncate font-semibold animate-pulse">
                  Loading...
                </p>
              </template>
              <template v-else>
                <div class="grid grid-cols-8" v-if="!inEditMode">
                  <p class="w-full col-span-6 text-slate-700 dark:text-slate-300 text-2xl truncate font-semibold">
                    {{presentationCardDetails.name}}
                  </p>
                  <DashButton v-if="editable" @click="openEditMode" class="col-span-1 rounded-l-full">
                    <Icon icon="heroicons-outline:pencil-square"></Icon>
                  </DashButton>
                  <DashButton v-if="editable" @click="deleteCard" class="col-span-1 rounded-r-full bg-danger-600">
                    <Icon icon="heroicons-outline:trash"></Icon>
                  </DashButton>

                </div>
                <div class="grid grid-cols-8" v-if="inEditMode">
                  <TextInput
                    class="col-span-6"
                    v-if="inEditMode"
                    label="Name"
                    type="text"
                    placeholder="John Doe"
                    name="name"
                    v-model="name"
                    :error="nameError"
                  />
                  <DashButton v-if="inEditMode" @click="submitCardDetails" class="col-span-2 justify-self-end my-auto rounded-full">
                    <Icon icon="heroicons-outline:check"></Icon>
                  </DashButton>
                </div>
              </template>

            </div>
            <div class="col-span-1 p-3">
              <template v-if="loading">
                <p class="w-full col-span-6 text-slate-700 dark:text-slate-300 text-2xl truncate font-semibold animate-pulse">
                  Loading...
                </p>
              </template>
              <template v-else>
                <p v-if="!inEditMode" class="dark:text-slate-300 text-slate-700 inline-block">{{presentationCardDetails.bio}}</p>
                <TextInput
                  v-if="inEditMode"
                  label="Biography"
                  type="text"
                  :placeholder="`I started volunteering at ${ COMMON_NAME } when...`"
                  name="bio"
                  v-model="bio"
                  :error="bioError"
                />
              </template>
            </div>
          </div>
        </div>
      </div>
    </form>
  </Card>
</template>

<style scoped lang="scss">

</style>
