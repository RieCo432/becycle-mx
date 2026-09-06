<template>
    <div class="grid grid-cols-12 gap-5">
      <div class="lg:col-span-6 col-span-12 row-span-2" v-if="aboutUsHtml !== null || editAllowed">
        <Card :title="`Welcome to ${COMMON_NAME}`">
          <div class="h-full">
            <div class="grid grid-cols-12 gap-5">
              <div class="col-span-12">
                <QuillEditor
                    v-if="editorActive && !editorHtmlMode"
                    toolbar="full"
                    v-model:content="quillContent"
                    content-type="html"/>
                <QuillEditor
                    v-if="editorActive && editorHtmlMode"
                    toolbar="full"
                    v-model:content="quillContent"
                    content-type="text"/>
                <div v-if="!editorActive" v-html="aboutUsHtml" class="dark:text-slate-300 text-slate-700 h-full"/>
              </div>
              <div v-if="!editorActive && editAllowed" class="col-span-2 col-end-13 mt-auto">
                <DashButton class="w-full" @click="openEditor">Edit</DashButton>
              </div>
            </div>
            <div v-if="editorActive && editAllowed" class="grid grid-cols-3 col-span-full gap-5 justify-items-stretch mt-20">
              <div class="col-span-full">
                <DashButton class="w-full" @click="openPhotoManager">Photos</DashButton>
              </div>
              <div  class="justify-self-start">
                <DashButton class="w-full btn-danger" @click="cancelEditor">Cancel</DashButton>
              </div>
              <div class="justify-self-center my-auto">
                <div class="grid grid-cols-3">
                  <div class="col-span-1 justify-items-end">
                    <span class="text-slate-700 dark:text-slate-300">WYSIWYG</span>
                  </div>
                  <div class="col-span-1 justify-items-center">
                    <Switch
                        v-model:model-value="editorHtmlMode"
                        class="w-auto"
                        badge
                        icon
                        next-icon="heroicons-outline:document-text"
                        prev-icon="heroicons-outline:code-bracket"/>
                  </div>
                  <div class="col-span-1 justify-items-start">
                    <span class="text-slate-700 dark:text-slate-300">HTML</span>
                  </div>
                </div>
              </div>
              <div  class="justify-self-end mt-auto">
                <DashButton class="w-full" @click="saveEditor">Save</DashButton>
              </div>
            </div>
          </div>
        </Card>
      </div>
        <div class="lg:col-span-6 col-span-12">
            <Card title="Quick Info">
                <div class="grid grid-cols-12 h-full gap-5">
                  <div class="col-span-12">
                    <p class="text-base text-slate-700 dark:text-slate-300">
                      {{QUICK_INFO }}</p><br>
                    <p class="text-base text-slate-700 dark:text-slate-300" v-if="!loadingAddress">
                        We are located at:<br>
                        {{ address.number }} {{ address.street }}<br>
                        {{ address.postcode }}, {{ address.city }}
                    </p>
                    <p class="text-base text-slate-700 dark:text-slate-300 animate-pulse" v-else>
                      We are located at:<br>
                      Loading...<br>
                      Loading...
                    </p>
                    <br>
                    <span
                        v-if="PAYPAL_BUTTON_ID"
                        class="text-base text-slate-700 dark:text-slate-300">You can donate to our cause via PayPal:</span><br>
                      <div id="donate-button-container">
                        <div id="donate-button"></div>
                      </div>
                    <p
                        v-if="FACEBOOK_LINK || INSTAGRAM_LINK"
                        class="text-base text-slate-700 dark:text-slate-300">You can contact us directly on social media:<br>
                      <a
                          v-if="FACEBOOK_LINK"
                          :href="FACEBOOK_LINK">
                          <img src="/src/assets/images/social/Facebook_Logo_Primary.png"
                               class="w-[32px] h-[32px] m-[16px] inline" alt="Facebook"/></a>
                      <a
                          v-if="INSTAGRAM_LINK"
                          :href="INSTAGRAM_LINK">
                          <img src="/src/assets/images/social/Instagram_Glyph_Gradient.png"
                               class="w-[32px] h-[32px] m-[16px] inline" alt="Instagram"/></a>
                    </p>
                  </div>
                </div>
            </Card>
        </div>
        <div class="lg:col-span-6 col-span-12">
            <Card title="Opening Days and Times">
              <div class="grid grid-cols-12 gap-5">
                <div class="col-span-12">
                  <Calendar
                      v-if="!loadingOpenDays"
                      expanded
                      :is-dark="themeSettingsStore.isDark"
                      :columns="numCalendarColumns"
                      :step="1"
                      :attributes="calendarAttributes"
                      :first-day-of-week="2"
                      :min-date="new Date()"/>
                  <div v-else class="rounded-md h-64 animate-pulse items-center bg-[#C4C4C4] dark:bg-slate-500 mx-auto"></div>
                </div>
                <div class="col-span-12">
                  <vue-good-table
                      v-if="!loadingOpeningTimes"
                      :columns="columns"
                      :rows="openingTimes"
                      style-class="vgt-table"
                      :sort-options="{
                    enabled: false
                  }"/>
                  <div v-else>
                    <TableSkeleton num-columns="3" count="2"></TableSkeleton>
                  </div>
                </div>
              </div>
            </Card>
        </div>
      <Modal title="Photo Manager" :active-modal="photoManagerOpen" @close="photoManagerOpen = false" size-class="max-w-[1000px]">
        <div class="grid grid-cols-6 gap-4">
          <div class="col-span-full">
            <p class="text-slate-700 dark:text-slate-300">
              Click on a photo to copy it to your clipboard. You can then paste it into the editor.
            </p>
          </div>

          <div class="col-span-full max-h-[55vh] overflow-y-auto">
            <div class="grid grid-cols-6 gap-4">
              <div
                v-for="photo in photos.sort((a, b) => new Date(b.createdOn) - new Date(a.createdOn))"
                :key="photo.id"
                class="col-span-1">

                <div class="relative inline-block w-full">
                  <DashButton
                    @click="() => deletePhoto(photo.id)"
                    class="absolute top-0 right-0 z-10 rounded-full bg-danger-500 dark:bg-danger-500 shadow-lg"
                  >
                    <Icon icon="heroicons-outline:trash"/>
                  </DashButton>
                  <div class="w-full h-auto rounded-md p-4">
                    <img
                      :src="photo.thumbnailUrl"
                      alt="Photo Thumbnail"
                      class="w-full h-full object-cover"
                      @click="() => copyPhoto(photo)">
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-span-full">
            <div class="h-full">
              <div
                v-bind="getRootProps()"
                class="w-full h-full text-center border rounded flex flex-col justify-center items-center
                border-secondary-500 border-dashed"
              >
                <div v-if="filesToUpload.length === 0" class="h-full w-full">
                  <input v-bind="getInputProps()" class="hidden"/>
                  <img src="../assets/images/svg/upload.svg" alt="" class="mx-auto mb-4"/>
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
          </div>
        </div>
      </Modal>
    </div>
</template>

<script>
import requests from '@/requests';
import Card from '@/components/Card';
import DashButton from '@/components/Button/index.vue';
import {useCredentialsStore} from '@/store/credentialsStore';
import {useThemeSettingsStore} from '@/store/themeSettings';
import {Calendar} from 'v-calendar';
import 'v-calendar/style.css';
import {useScreens} from 'vue-screen-utils';
import TableSkeleton from '@/components/Skeleton/TableSkeleton.vue';
import {QuillEditor} from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import {useToast} from 'vue-toastification';
import Switch from '@/components/Switch';
import Modal from '@/components/Modal/Modal.vue';
import {Icon} from '@iconify/vue';
import {useDropzone} from 'vue3-dropzone';
import {ref} from 'vue';

const COMMON_NAME = import.meta.env.VITE_COMMON_NAME;
const QUICK_INFO = import.meta.env.VITE_QUICK_INFO;
const FACEBOOK_LINK = import.meta.env.VITE_FACEBOOK_LINK;
const INSTAGRAM_LINK = import.meta.env.VITE_INSTAGRAM_LINK;
const PAYPAL_BUTTON_ID = import.meta.env.VITE_PAYPAL_DONATE_BUTTON_ID;

const credentialsStore = useCredentialsStore();
const themeSettingsStore = useThemeSettingsStore();
const toast = useToast();
const {mapCurrent} = useScreens({
  xs: '0px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  xxl: '1536px',
});

export default {
  components: {
    Modal,
    Switch,
    TableSkeleton,
    DashButton,
    Card,
    Calendar,
    QuillEditor,
    Icon,
  },
  setup() {
    const filesToUpload = ref([]);
    const photos = ref([]);

    function pushPhotoObject(photo) {
      requests.getPhotoThumbnail(photo.id).then((response) => {
        const blob = new Blob([response.data], {type: response.headers['content-type']});
        photos.value.push({
          id: photo.id,
          createdOn: new Date(photo.createdOn),
          userId: photo.userId,
          thumbnailBlob: blob,
          contentType: response.headers['content-type'],
          thumbnailUrl: window.URL.createObjectURL(blob),
        });
      });
    }
    function onDrop(acceptFiles) {
      filesToUpload.value = acceptFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
          contentType: file.type,
        }),
      );
      requests.postNewPhotos(filesToUpload.value).then((response) => {
        toast.success('Photos uploaded successfully', {timeout: 2000});
        filesToUpload.value = [];
        response.data.forEach((photoId) => {
          pushPhotoObject(photoId);
        });
      });
    }
    const {getRootProps, getInputProps, ...rest} = useDropzone({onDrop, multiple: true});

    return {
      photos,
      filesToUpload,
      pushPhotoObject,
      getRootProps,
      getInputProps,
      ...rest,
    };
  },
  data() {
    return {
      COMMON_NAME: COMMON_NAME,
      QUICK_INFO: QUICK_INFO,
      FACEBOOK_LINK: FACEBOOK_LINK,
      INSTAGRAM_LINK: INSTAGRAM_LINK,
      PAYPAL_BUTTON_ID: PAYPAL_BUTTON_ID,
      loadingOpeningTimes: true,
      loadingOpenDays: true,
      loadingAddress: true,
      openingTimes: null,
      address: null,
      editAllowed: false,
      editorActive: false,
      editorHtmlMode: false,
      aboutUsHtml: null,
      quillContent: null,
      themeSettingsStore: themeSettingsStore,
      calendarAttributes: [{
        key: 'default-look',
        dates: {repeat: {every: 'day'}},
        content: {
          class: 'opacity-20',
        },
      }],
      numCalendarColumns: mapCurrent({xs: 1, sm: 2, md: 2, lg: 1, xxl: 2}, 1),
      columns: [
        {
          label: 'Day',
          field: 'day',
        },
        {
          label: 'Open',
          field: 'open',
        },
        {
          label: 'Close',
          field: 'close',
        },
      ],
      photoManagerOpen: false,
    };
  },
  methods: {

    openEditor() {
      this.quillContent = this.aboutUsHtml;
      this.editorActive = true;
    },
    cancelEditor() {
      this.editorActive = false;
    },
    saveEditor() {
      requests.patchAboutUs(this.quillContent).then((response) => {
        this.aboutUsHtml = response.data.html;
        this.editorActive = false;
        toast.success('About Us Updated!', {timeout: 1000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    },
    openPhotoManager() {
      requests.getPhotos().then((response) => {
        this.photos = [];
        for (const photo of response.data) {
          this.pushPhotoObject(photo);
        }
        this.photoManagerOpen = true;
      });
    },
    async copyPhoto(photo) {
      const url = `${requests.getApiBaseUrl()}/public/photos/${photo.id}`;

      const html = `<img src="${url}" alt="photo">`;
      
      if (this.editorHtmlMode) {
        await navigator.clipboard.writeText(html);
      } else {
        const item = {
          'text/html': new Blob([html], {type: 'text/html'}),
        };
        const clipboardItem = new ClipboardItem(item);
        await navigator.clipboard.write([clipboardItem]);
      }

      this.photoManagerOpen = false;
      toast.success('Photo copied to clipboard', {timeout: 2000});
    },
    loadAsync(url, callback) {
      const s = document.createElement('script');
      s.setAttribute('src', url); s.onload = callback;
      document.head.insertBefore(s, document.head.firstElementChild);
    },
    deletePhoto(photoId) {
      requests.deletePhoto(photoId)
        .then(() => {
          this.photos = this.photos.filter((photo) => photo.id !== photoId);
          toast.success('Photo deleted', {timeout: 2000});
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    },
  },
  mounted() {
    if (credentialsStore.getTokenType() === 'user') {
      requests.getUserMe().then((response) => {
        this.editAllowed = response.data.appointmentManager;
      });
    }
    requests.getAboutUs().then((response) => {
      this.aboutUsHtml = response.data.html;
    });
    requests.getOpeningTimes().then((response) => {
      this.openingTimes = response.data;
      this.loadingOpeningTimes = false;
    });
    requests.getUpcomingOpenDates().then((response) => {
      this.calendarAttributes = [];
      this.calendarAttributes = response.data.map((openDay, index) => {
        const utcDate = new Date(`${openDay}T00:00:00Z`);
        return {
          key: `openDay-${index}`,
          dates: utcDate,
          content: {class: 'opacity-100'},
          highlight: {color: 'white', fillMode: 'outline'},
        };
      });
      this.loadingOpenDays = false;
    });
    requests.getAddress().then((response) => {
      this.address = response.data;
      this.loadingAddress = false;
    });
    if (PAYPAL_BUTTON_ID) {
      this.loadAsync('https://www.paypalobjects.com/donate/sdk/donate-sdk.js', function() {
        // eslint-disable-next-line new-cap
        PayPal.Donation.Button({
          env: 'production',
          hosted_button_id: PAYPAL_BUTTON_ID,
          image: {
            src: 'https://www.paypalobjects.com/en_GB/i/btn/btn_donate_LG.gif',
            alt: 'Donate with PayPal button',
            title: 'PayPal - The safer, easier way to pay online!',
          },
        }).render('#donate-button');
      });
    }
  },
  created() {
    this.loadAsync('https://app.termly.io/resource-blocker/cfac8041-9e2d-4f64-9c8b-1ba418ea07a1?autoBlock=on');
  },
};

</script>
<style lang=""></style>
