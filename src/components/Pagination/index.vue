<template>
  <div class="md:flex md:space-y-0 space-y-5" :class="wrapperClass">
    <div
      class="flex items-center space-x-4 rtl:space-x-reverse"
      v-if="enableSearch"
      :class="searchClasss"
    >
      <div
        class="flex items-center space-x-2 rtl:space-x-reverse"
        v-if="enableSearch && enableInput"
      >
        <input
          v-model.number="input"
          class="form-control w-9 overflow-auto h-9"
          type="text"
          placeholder="0"
        />
        <div
          @click.prevent="changePage(input)"
          class="flex-0 cursor-pointer text-sm h-9 w-9 bg-slate-900 text-white flex items-center justify-center rounded"
        >
          Go
        </div>
      </div>

      <div class="flex items-center" v-if="enableSearch && enableSelect">
        <Select
          v-model.number="input2"
          @change="changePage(input2)"
          placeholder="Go"
          classInput=" w-[60px] h-9 "
          :options="options"
        >
        </Select>

        <span class="text-sm text-slate-500 inline-block ltr:ml-2 rtl:mr-2">
          of {{ perPage }} entries</span
        >
      </div>
    </div>
    <ul class="pagination" :class="paginationClass">
      <li
        class="text-xl leading-4 text-slate-900 dark:text-white rtl:rotate-180"
      >
        <button
          @click.prevent="changePage(prevPage)"
          :disabled="current === 1"
          :class="current === 1 ? ' opacity-50 cursor-not-allowed' : ''"
        >
          <Icon icon="heroicons-outline:chevron-left" v-if="!enableText" />
          <span v-if="enableText" class="text-sm inline-block rtl:-rotate-180"
            >Previous</span
          >
        </button>
      </li>
      <li class="" v-if="hasFirst()">
        <button @click.prevent="changePage(1)">
          <div>
            <span> 1 </span>
          </div>
        </button>
      </li>
      <li class="text-slate-600 dark:text-slate-300" v-if="hasFirst()">...</li>
      <li class="" v-for="(page, i) in pages" :key="i">
        <button @click.prevent="changePage(page)">
          <div
            :class="{
              active: current === page,
            }"
            class=""
          >
            <span class="">{{ page }}</span>
          </div>
        </button>
      </li>
      <li class="text-slate-600 dark:text-slate-300" v-if="hasLast()">...</li>
      <li class="" v-if="hasLast()">
        <button @click.prevent="changePage(totalPages)">
          <div>
            <span> {{ totalPages }} </span>
          </div>
        </button>
      </li>
      <li
        class="text-xl leading-4 text-slate-900 dark:text-white rtl:rotate-180"
      >
        <button
          @click.prevent="changePage(nextPage)"
          :disabled="current === totalPages"
          :class="
            current === totalPages ? ' opacity-50 cursor-not-allowed' : ''
          "
        >
          <Icon icon="heroicons-outline:chevron-right" v-if="!enableText" />
          <span v-if="enableText" class="text-sm rtl:-rotate-180 inline-block"
            >Next</span
          >
        </button>
      </li>
    </ul>
  </div>
</template>

<script>
import Icon from "@/components/Icon";
import Select from "@/components/Select";
import { defineComponent } from "vue";
export default defineComponent({
  name: "Pagination",
  components: {
    Icon,
    Select,
  },
  props: {
    options: {
      type: Array,
      default: () => [{}],
    },
    enableText: {
      type: Boolean,
      default: false,
    },
    enableInput: {
      type: Boolean,
      default: false,
    },
    enableSelect: {
      type: Boolean,
      default: false,
    },
    enableSearch: {
      type: Boolean,
      default: false,
    },
    pageChanged: {
      type: Function,
    },
    perPageChanged: {
      type: Function,
    },
    current: {
      type: Number,
      default: 1,
    },
    total: {
      type: Number,
      default: 0,
    },
    perPage: {
      type: Number,
      default: 10,
    },
    pageRange: {
      type: Number,
      default: 2,
    },
    textBeforeInput: {
      type: String,
      default: "Go to page",
    },
    textAfterInput: {
      type: String,
      default: "Go",
    },
    paginationClass: {
      type: String,
      default: "default",
    },
    searchClasss: {
      type: String,
      default: "default",
    },
    wrapperClass: {
      type: String,
      default: "justify-between",
    },
  },
  data() {
    return {
      input: "",
      input2: null,
    };
  },
  methods: {
    hasFirst: function () {
      return this.rangeStart !== 1;
    },
    hasLast: function () {
      return this.rangeEnd < this.totalPages;
    },
    hasPrev: function () {
      return this.current > 1;
    },
    hasNext: function () {
      return this.current < this.totalPages;
    },
    changePage: function (page) {
      if (page > 0 && page <= this.totalPages) {
        this.$emit("page-changed", page);
      }
      if (this.pageChanged) {
        this.pageChanged({ currentPage: page });
      }
    },
    customPerPageChange(page) {
      this.perPageChanged({ currentPerPage: page });
    },
  },
  computed: {
    pages: function () {
      var pages = [];

      for (var i = this.rangeStart; i <= this.rangeEnd; i++) {
        pages.push(i);
      }

      return pages;
    },
    rangeStart: function () {
      var start = this.current - this.pageRange;

      return start > 0 ? start : 1;
    },
    rangeEnd: function () {
      var end = this.current + this.pageRange;

      return end < this.totalPages ? end : this.totalPages;
    },
    totalPages: function () {
      return Math.ceil(this.total / this.perPage);
    },
    nextPage: function () {
      return this.current + 1;
    },
    prevPage: function () {
      return this.current - 1;
    },
  },
});
</script>

<style scoped lang="scss">
.pagination {
  @apply flex items-center space-x-4 flex-wrap rtl:space-x-reverse;
  li {
    a,
    div {
      @apply bg-slate-100 dark:bg-slate-700 dark:text-slate-400 text-slate-900 text-sm font-normal rounded leading-[16px] flex h-6 w-6 items-center justify-center transition-all duration-150;
      &.active {
        @apply bg-slate-900 dark:bg-slate-600  dark:text-slate-200 text-white font-medium;
      }
    }
  }
  &.bordered {
    @apply border border-[#D8DEE6] rounded-[3px] py-1 px-2;
    li {
      @apply text-slate-500;
      &:first-child,
      &:last-child {
        button {
          @apply hover:bg-slate-900 hover:text-white transition duration-150 text-slate-500 h-6 w-6 flex items-center justify-center rounded;
        }
      }
      a,
      div {
        @apply bg-transparent text-slate-500;
        &.active {
          @apply bg-slate-900 text-white;
        }
      }
    }
  }
  &.border-group {
    @apply border border-[#D8DEE6] rounded-[3px]  px-0 space-x-0 rtl:space-x-reverse;
    li {
      @apply border-r border-[#D8DEE5] h-full flex flex-col  justify-center px-3  last:border-none text-slate-500;
      a,
      div {
        @apply bg-transparent text-slate-500 dark:text-white h-auto w-auto;
        &.active {
          @apply text-slate-900 dark:text-white text-lg;
        }
      }
    }
  }
}
</style>
