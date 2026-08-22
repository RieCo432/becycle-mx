<script>
import Card from '@/components/Card/index.vue';
import DashButton from '@/components/Button/index.vue';
import Icon from '@/components/Icon/index.vue';
import requests from '@/requests';
import {useDropzone} from 'vue3-dropzone';
import {onMounted, ref, toRef} from 'vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'ContractPhotosCard',
  components: {Card, DashButton, Icon},
  props: {
    contractId: {
      type: String,
      required: true,
    },
  },
  setup(props, context) {
    const contractId = toRef(props, 'contractId');
    const filesToUpload = ref([]);
    const fileError = ref(null);
    const photoUrls = ref([]);
    const loadingContractPhotos = ref(false);

    function getContractPhoto(photoId) {
      requests.getContractPhotoUrl(contractId.value, photoId)
        .then((response) => {
          photoUrls.value.push(
            {
              id: photoId,
              url: window.URL.createObjectURL(new Blob([response.data], {type: response.headers['content-type']})),
            });
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    }

    function getContractPhotos() {
      loadingContractPhotos.value = true;
      requests.getContractPhotoIds(contractId.value)
        .then((response) => {
          for (const photoId of response.data) {
            getContractPhoto(photoId);
          }
          loadingContractPhotos.value = false;
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    }

    function deleteContractPhoto(photoId) {
      if (confirm('Are you sure you want to delete this photo?')) {
        requests.deleteContractPhoto(contractId.value, photoId).then((response) => {
          toast.success('Contract photo deleted successfully', {timeout: 2000});
          photoUrls.value.splice(photoUrls.value.findIndex((photoUrl) => photoUrl.id === photoId), 1);
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
      }
    }

    function openPhoto(url) {
      window.open(url, '_blank');
    }

    function onDrop(acceptFiles) {
      filesToUpload.value = acceptFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
          contentType: file.type,
        }),
      );
      requests.postNewContractPhotos(contractId.value, filesToUpload.value).then((response) => {
        toast.success('Contract photos uploaded successfully', {timeout: 2000});
        filesToUpload.value = [];
        response.data.forEach((photoId) => {
          getContractPhoto(photoId);
        });
      });
    }
    const {getRootProps, getInputProps, ...rest} = useDropzone({onDrop, multiple: true});

    onMounted(() => {
      getContractPhotos();
    });

    return {
      getInputProps,
      getRootProps,
      fileError,
      filesToUpload,
      ...rest,
      photoUrls,
      deleteContractPhoto,
      loadingContractPhotos,
      openPhoto,
    };
  },
};
</script>

<template>
  <template v-if="!loadingContractPhotos">
    <div class="col-span-12">
      <Card title="Photos">
        <div class="grid grid-cols-12 gap-5">
          <div v-for="photoUrl in photoUrls" class="col-span-4 lg:col-span-2 min-h-full" :key="photoUrl.id">
            <div class="relative inline-block w-full">
              <DashButton
                @click="() => deleteContractPhoto(photoUrl.id)"
                class="absolute top-0 right-0 z-10 rounded-full bg-danger-500 dark:bg-danger-500 shadow-lg"
              >
                <Icon icon="heroicons-outline:trash"/>
              </DashButton>
              <div class="w-full h-auto rounded-md p-4">
                <img :src="photoUrl.url" alt="Photo" class="w-full h-full" @click="() => openPhoto(photoUrl.url)"/>
              </div>

            </div>
          </div>
          <div class="col-span-4 lg:col-span-2 h-full">
            <div class="h-full">
              <div
                v-bind="getRootProps()"
                :class="'w-full h-full text-center border rounded flex flex-col justify-center items-center '
                    + (fileError ? 'border-danger-500 border-solid' : 'border-secondary-500 border-dashed')
                    "
              >
                <div v-if="filesToUpload.length === 0" class="h-full w-full">
                  <input v-bind="getInputProps()" class="hidden"/>
                  <img src="../../assets/images/svg/upload.svg" alt="" class="mx-auto mb-4"/>
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
                <div v-else class="flex w-full h-full justify-center align-middle">
                  <div v-for="fileToUpload in filesToUpload" :key="fileToUpload.name">
                    <img
                      v-if="fileToUpload.contentType.startsWith('image/')"
                      :src="fileToUpload.preview"
                      class="object-contain block rounded-md"
                      alt="Photo"
                    />
                  </div>
                </div>
              </div>
            </div>
            <!--                  <ErrorMessage name="file" :error="fileError" class="text-danger-500"/>-->
          </div>
        </div>
      </Card>
    </div>
  </template>
</template>
