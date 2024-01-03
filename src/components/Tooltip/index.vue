<template>
  <button
    v-if="!$slots.default"
    :content="content"
    v-tippy="{
      placement: placement,
      arrow: arrow,
      theme: theme,
      animation: animation,
      trigger: trigger,
      interactive: interactive,
      delay: delay,
      duration: duration,
      allowHTML: allowHTML,
      distance: distance,
      offset: offset,
      maxWidth: maxWidth,
    }"
    class="btn"
    :class="btnClass"
  >
    {{ title }}
  </button>

  <tippy
    :placement="placement"
    :arrow="arrow"
    :theme="theme"
    :animation="animation"
    :trigger="trigger"
    :interactive="interactive"
    :delay="delay"
    :duration="duration"
    :allowHTML="allowHTML"
    :maxWidth="maxWidth"
    :distance="distance"
    :offset="offset"
    v-if="$slots.default"
  >
    <button class="btn" :class="btnClass" v-if="!$slots.button">
      {{ title }}
    </button>

    <button v-if="$slots.button" class="inline-block">
      <slot name="button"></slot>
    </button>

    <template #content> <slot></slot> </template>
  </tippy>
</template>
<script>
import "tippy.js/animations/perspective-extreme.css";
import "tippy.js/animations/perspective-subtle.css";
import "tippy.js/animations/perspective.css";
import "tippy.js/animations/scale-extreme.css";
import "tippy.js/animations/scale-subtle.css";
import "tippy.js/animations/scale.css";
import "tippy.js/animations/shift-away-extreme.css";
import "tippy.js/animations/shift-away-subtle.css";
import "tippy.js/animations/shift-away.css";
import "tippy.js/animations/shift-toward-extreme.css";
import "tippy.js/animations/shift-toward-subtle.css";
import "tippy.js/animations/shift-toward.css";
import "tippy.js/dist/tippy.css";
import "tippy.js/themes/light.css";

export default {
  props: {
    title: {
      type: String,
      default: "Tooltip on top",
    },
    content: {
      type: String,
      default: "Tooltip on top!",
    },
    btnClass: {
      type: String,
      default: "btn-outline-dark",
    },
    placement: {
      type: String,
      default: "top",
    },
    arrow: {
      type: Boolean,
      default: false,
    },
    theme: {
      type: String,
      default: "",
    },
    animation: {
      type: String,
      default: "scale",
    },
    trigger: {
      type: String,
      default: "mouseenter",
    },
    interactive: {
      type: Boolean,
      default: false,
    },
    delay: {
      type: Number,
      default: 0,
    },
    duration: {
      type: Number,
      default: 200,
    },
    allowHTML: {
      type: Boolean,
      default: false,
    },
    maxWidth: {
      type: String,
      default: "",
    },
    distance: {
      type: String,
      default: "1rem",
    },
    offset: {
      type: Array,
      default: () => [0, 0],
    },
  },
};
</script>
<style lang="scss">
.tippy-box {
  @apply bg-slate-900;
}
.tippy-arrow {
  @apply text-slate-900;
}
.tippy-box[data-theme~="primary-500"] {
  @apply bg-primary-500 text-white;
}
.tippy-box[data-theme~="secondary-500"] {
  @apply bg-secondary-500 text-white;
}
.tippy-box[data-theme~="success-500"] {
  @apply bg-success-500 text-white;
}
.tippy-box[data-theme~="info-500"] {
  @apply bg-info-500 text-white;
}
.tippy-box[data-theme~="warning-500"] {
  @apply bg-warning-500 text-white;
}
.tippy-box[data-theme~="danger-500"] {
  @apply bg-danger-500 text-white;
}
.tippy-box[data-theme~="dark"] {
  @apply bg-slate-900 text-white dark:bg-slate-900;
}
.tippy-box[data-theme~="custom-light"] {
  @apply bg-white text-slate-900 dark:bg-slate-700 shadow-dropdown dark:border-slate-700 dark:border;
}
.tippy-box[data-theme~="custom-light2"] {
  @apply bg-white text-slate-900 dark:bg-slate-700 shadow-dropdown dark:border-slate-700 dark:border rounded;
  .tippy-content {
    @apply p-0;
  }
}

.tippy-box[data-theme~="custom-light"][data-placement^="top"]
  > .tippy-arrow::before {
  @apply border-t-white dark:border-t-slate-700;
}
.tippy-box[data-theme~="custom-light"][data-placement^="bottom"]
  > .tippy-arrow::before {
  @apply border-b-white dark:border-b-slate-700;
}
.tippy-box[data-theme~="custom-light"][data-placement^="left"]
  > .tippy-arrow::before {
  @apply border-l-white dark:border-l-slate-700;
}
.tippy-box[data-theme~="custom-light"][data-placement^="right"]
  > .tippy-arrow::before {
  @apply border-r-white dark:border-r-slate-700;
}

.tippy-box[data-theme~="primary-500"][data-placement^="top"]
  > .tippy-arrow::before {
  @apply border-t-primary-500;
}
.tippy-box[data-theme~="primary-500"][data-placement^="bottom"]
  > .tippy-arrow::before {
  @apply border-b-primary-500;
}
.tippy-box[data-theme~="primary-500"][data-placement^="left"]
  > .tippy-arrow::before {
  @apply border-l-primary-500;
}
.tippy-box[data-theme~="primary-500"][data-placement^="right"]
  > .tippy-arrow::before {
  @apply border-r-primary-500;
}
.tippy-box[data-theme~="secondary-500"][data-placement^="top"]
  > .tippy-arrow::before {
  @apply border-t-secondary-500;
}
.tippy-box[data-theme~="secondary-500"][data-placement^="bottom"]
  > .tippy-arrow::before {
  @apply border-b-secondary-500;
}
.tippy-box[data-theme~="secondary-500"][data-placement^="left"]
  > .tippy-arrow::before {
  @apply border-l-secondary-500;
}
.tippy-box[data-theme~="secondary-500"][data-placement^="right"]
  > .tippy-arrow::before {
  @apply border-r-secondary-500;
}
.tippy-box[data-theme~="success-500"][data-placement^="top"]
  > .tippy-arrow::before {
  @apply border-t-success-500;
}
.tippy-box[data-theme~="success-500"][data-placement^="bottom"]
  > .tippy-arrow::before {
  @apply border-b-success-500;
}
.tippy-box[data-theme~="success-500"][data-placement^="left"]
  > .tippy-arrow::before {
  @apply border-l-success-500;
}
.tippy-box[data-theme~="success-500"][data-placement^="right"]
  > .tippy-arrow::before {
  @apply border-r-success-500;
}
.tippy-box[data-theme~="info-500"][data-placement^="top"]
  > .tippy-arrow::before {
  @apply border-t-info-500;
}
.tippy-box[data-theme~="info-500"][data-placement^="bottom"]
  > .tippy-arrow::before {
  @apply border-b-info-500;
}
.tippy-box[data-theme~="info-500"][data-placement^="left"]
  > .tippy-arrow::before {
  @apply border-l-info-500;
}
.tippy-box[data-theme~="info-500"][data-placement^="right"]
  > .tippy-arrow::before {
  @apply border-r-info-500;
}
.tippy-box[data-theme~="warning-500"][data-placement^="top"]
  > .tippy-arrow::before {
  @apply border-t-warning-500;
}
.tippy-box[data-theme~="warning-500"][data-placement^="bottom"]
  > .tippy-arrow::before {
  @apply border-b-warning-500;
}
.tippy-box[data-theme~="warning-500"][data-placement^="left"]
  > .tippy-arrow::before {
  @apply border-l-warning-500;
}
.tippy-box[data-theme~="warning-500"][data-placement^="right"]
  > .tippy-arrow::before {
  @apply border-r-warning-500;
}
.tippy-box[data-theme~="danger-500"][data-placement^="top"]
  > .tippy-arrow::before {
  @apply border-t-danger-500;
}
.tippy-box[data-theme~="danger-500"][data-placement^="bottom"]
  > .tippy-arrow::before {
  @apply border-b-danger-500;
}
.tippy-box[data-theme~="danger-500"][data-placement^="left"]
  > .tippy-arrow::before {
  @apply border-l-danger-500;
}
.tippy-box[data-theme~="danger-500"][data-placement^="right"]
  > .tippy-arrow::before {
  @apply border-r-danger-500;
}

.tippy-box[data-theme~="dark"][data-placement^="top"] > .tippy-arrow::before {
  @apply border-t-black-500 dark:border-t-slate-900;
}
.tippy-box[data-theme~="dark"][data-placement^="bottom"]
  > .tippy-arrow::before {
  @apply border-b-black-500 dark:border-b-slate-900;
}
.tippy-box[data-theme~="dark"][data-placement^="left"] > .tippy-arrow::before {
  @apply border-l-black-500 dark:border-l-slate-900;
}
.tippy-box[data-theme~="dark"][data-placement^="right"] > .tippy-arrow::before {
  @apply border-r-black-500 dark:border-r-slate-900;
}
</style>
