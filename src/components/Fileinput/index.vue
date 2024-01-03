<template>
  <div>
    <div class="filegroup">
      <label :for="name">
        <input
          type="file"
          @change="onChange"
          class="bg-red-400 w-full hidden"
          :id="name"
          :name="name"
          :multiple="multiple"
          :preview="preview"
          :placeholder="placeholder"
          :label="label"
        />
        <div
          class="w-full h-[40px] file-control flex items-center"
          :class="`  ${classInput}`"
        >
          <span
            v-if="!multiple"
            class="flex-1 overflow-hidden text-ellipsis whitespace-nowrap"
          >
            <span
              v-if="selectedFile?.name"
              :class="
                filenametag ? ' badge-title' : 'text-slate-900 dark:text-white'
              "
              >{{ selectedFile?.name }}</span
            >
            <span v-if="!selectedFile?.name" class="text-slate-400">{{
              placeholder
            }}</span>
          </span>

          <span
            v-if="multiple"
            class="flex-1 overflow-hidden text-ellipsis whitespace-nowrap"
          >
            <span
              v-if="multipleurls.length > 0"
              :class="
                filenametag ? ' badge-title' : 'text-slate-900 dark:text-white'
              "
              >{{
                multipleurls.length > 0
                  ? multipleurls.length + " files selected"
                  : ""
              }}</span
            >
            <span
              class="text-slate-400"
              v-if="placeholder && multipleurls.length === 0"
            >
              {{ placeholder }}</span
            >
          </span>
          <span
            class="file-name flex-none cursor-pointer border-l px-4 border-slate-200 dark:border-slate-700 h-full inline-flex items-center bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 text-base rounded-tr rounded-br font-normal"
            >{{ label }}</span
          >
        </div>

        <div
          v-if="url && !multiple && preview"
          class="w-[200px] h-[200px] mx-auto mt-6"
        >
          <img
            :src="url"
            class="w-full object-cover h-full block rounded"
            :alt="selectedFile?.name"
          />
        </div>

        <div
          class="flex flex-wrap space-x-5 rtl:space-x-reverse"
          v-if="multipleurls.length > 0 && multiple && preview"
        >
          <div
            v-for="(url, index) in multipleurls"
            :key="index"
            class="xl:w-1/5 md:w-1/3 w-1/2 rounded mt-6"
          >
            <img
              :src="url"
              class="object-cover w-full h-full rounded"
              :alt="selectedFile?.name"
            />
          </div>
        </div>
      </label>
    </div>
  </div>
</template>
<script>
export default {
  name: "Fileinput",
  props: {
    name: {
      type: String,
      default: "name",
    },
    multiple: {
      type: Boolean,
      default: false,
    },
    preview: {
      type: Boolean,
      default: false,
    },
    placeholder: {
      type: String,
      default: "Choose a file or drop it here...",
    },
    label: {
      type: String,
      default: "Browse",
    },
    classInput: {
      type: String,
      default: "",
    },
    filenametag: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      selectedFile: null,
      url: null,
      multipleFiles: [],
      multipleurls: [],
    };
  },
  methods: {
    onChange(e) {
      this.selectedFile = e.target.files[0];
      this.url = URL.createObjectURL(this.selectedFile);
      this.multipleFiles = Array.from(e.target.files);
      this.multipleFiles.forEach((file) => {
        this.multipleurls.push(URL.createObjectURL(file));
      });

      this.$emit("input", this.selectedFile);
    },
  },
};
</script>
<style lang="scss">
.file-control {
  @apply bg-transparent dark:bg-slate-900 dark:text-white transition duration-300 ease-in-out border border-slate-200 dark:border-slate-700 focus:ring-1 focus:ring-slate-900 dark:focus:ring-slate-900 focus:outline-none focus:ring-opacity-90 rounded   text-sm ltr:pl-3 rtl:pr-3   placeholder:font-normal;
}
.badge-title {
  @apply bg-slate-900 text-white px-2 py-[3px] rounded text-sm;
}
</style>
