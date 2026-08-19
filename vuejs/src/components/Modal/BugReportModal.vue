<template>
  <Modal :title="this.$store.bugReportingStore.modalTitle"
         :activeModal="activeModal"
         @close="this.$store.bugReportingStore.closeModal">
    <form @submit.prevent="submitBugReport">
      <div class="grid grid-cols-12 gap-2">
        <div class="col-span-12">
          <Textarea
              v-model="description"
              type="text"
              label="Description"
              placeholder="Description"
              name="description"
              :rows="6"
              :error="descriptionError"
          />
        </div>
        <div v-if="id != null" class="col-span-12">
          <Textarea
              v-model="consoleHistory"
              type="text"
              label="Console History"
              placeholder="Console History"
              name="consoleHistory"
              :isReadonly="true"
              :rows="20"
          />
        </div>
        <div class="col-span-12">
          <DashButton type="submit" class="btn-sm mx-auto block-btn" :text="submitButtonText"/>
        </div>
      </div>
    </form>
  </Modal>
</template>

<script>
import Modal from "@/components/Modal/Modal.vue";
import DashButton from "@/components/Button/index.vue";
import Textarea from "@/components/Textarea/index.vue";
import TextInput from "@/components/TextInput/index.vue";
import requests from "@/requests";
import * as yup from "yup";
import {useField, useForm} from "vee-validate";
import {ref} from "vue";
import {useToast} from "vue-toastification";

const toast = useToast();

export default {
  name: "BugReportModal",
  components: {TextInput, Textarea, DashButton, Modal},
  setup(props, context) {
    const id = ref(null);
    const bugReportSchema = yup.object().shape({
      description: yup.string().max(1024).required('Description is required'),
    });

    const {handleSubmit, resetForm} = useForm({
      validationSchema: bugReportSchema,
      keepValuesOnUnmount: false,
    });

    const {value: description, errorMessage: descriptionError} = useField('description');

    const submitBugReport = handleSubmit((values) => {
      if (id.value == null) {
        requests.createBugReport({
          description: values.description,
          pageAddress: window.location.href,
          consoleHistory: localStorage.getItem("bugReportConsoleHistory"),
        }).then((response) => {
          toast.success('Bug report created', {timeout: 2000});
          context.emit('bugReportSubmitted', response.data);
          resetForm()
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        })
      } else {
        requests.patchBugReport({id: id.value, description: values.description}).then((response) => {
          toast.success('Bug report updated', {timeout: 2000});
          context.emit('bugReportSubmitted', response.data);
          resetForm()
        }).catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        })
      }
    });
    return {
      id,
      description,
      descriptionError,
      submitBugReport,
      resetForm
    };
  },
  computed: {
    submitButtonText() {
      return this.$store.bugReportingStore.bugReport.id == null ? 'Submit Bug Report' : 'Update Bug Report';
    },
    activeModal() {
      return this.$store.bugReportingStore.modalVisible
    }
  },
  watch: {
    activeModal(newValue) {
      this.resetForm()
      if (!newValue)
        return;
      this.id = this.$store.bugReportingStore.bugReport.id;
      if(this.id == null)
        return

      this.description = this.$store.bugReportingStore.bugReport.description;
      this.consoleHistory = this.$store.bugReportingStore.bugReport.consoleHistory != null
          ? JSON.stringify(JSON.parse(this.$store.bugReportingStore.bugReport.consoleHistory), null, 2) : null
    }
  }
}
</script>

<style scoped lang="scss">

</style>