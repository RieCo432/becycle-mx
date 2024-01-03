<template>
  <div
    class="fromGroup relative"
    :class="`${error ? 'has-error' : ''}  ${horizontal ? 'flex' : ''} ${
      validate ? 'is-valid' : ''
    } `"
  >
    <label
      v-if="label"
      :class="`${classLabel}  ${
        horizontal ? 'flex-0 mr-6 md:w-[100px] w-[60px] break-words' : ''
      }  ltr:inline-block rtl:block  input-label `"
      :for="name"
    >
      {{ label }}</label
    >
    <div class="relative" :class="horizontal ? 'flex-1' : ''">
      <textarea
        :name="name"
        :placeholder="placeholder"
        :class="`${classInput} input-control block w-full focus:outline-none pt-3 `"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :error="error"
        :id="name"
        :readonly="isReadonly"
        :disabled="disabled"
        :rows="rows"
        :validate="validate"
      ></textarea>

      <div
        class="flex text-xl absolute ltr:right-[14px] rtl:left-[14px] top-1/2 -translate-y-1/2"
      >
        <span v-if="error" class="text-danger-500">
          <Icon icon="heroicons-outline:information-circle" />
        </span>

        <span v-if="validate" class="text-success-500">
          <Icon icon="bi:check-lg" />
        </span>
      </div>
    </div>

    <span
      v-if="error"
      class="mt-2"
      :class="
        msgTooltip
          ? ' inline-block bg-danger-500 text-white text-[10px] px-2 py-1 rounded'
          : ' text-danger-500 block text-sm'
      "
      >{{ error }}</span
    >
    <span
      v-if="validate"
      class="mt-2"
      :class="
        msgTooltip
          ? ' inline-block bg-success-500 text-white text-[10px] px-2 py-1 rounded'
          : ' text-success-500 block text-sm'
      "
      >{{ validate }}</span
    >
    <span
      class="block text-secondary-500 font-light leading-4 text-xs mt-2"
      v-if="description"
      >{{ description }}</span
    >
  </div>
</template>
<script>
import Icon from "@/components/Icon";
export default {
  components: {
    Icon,
  },
  props: {
    placeholder: {
      type: String,
      default: "message",
    },
    label: {
      type: String,
    },
    classLabel: {
      type: String,
      default: " ",
    },
    classInput: {
      type: String,
      default: "classinput",
    },

    name: {
      type: String,
    },
    modelValue: {
      type: String,
      default: "",
    },
    error: {
      type: String,
    },

    isReadonly: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    rows: {
      type: Number,
      default: 3,
    },
    horizontal: {
      type: Boolean,
      default: false,
    },
    validate: {
      type: String,
    },
    msgTooltip: {
      type: Boolean,
      default: false,
    },
    description: {
      type: String,
    },
  },
  data() {
    return {
      types: this.type,
    };
  },
  methods: {
    toggleType() {
      // toggle the type of the input field
      this.types = this.types === "text" ? "password" : "text";
    },
  },
};
</script>
<style lang="scss"></style>
