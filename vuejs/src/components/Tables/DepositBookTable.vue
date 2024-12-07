<template>
  <div>
    <Card noborder>
      <div
          class="md:flex justify-between pb-6 md:space-y-0 space-y-3 items-center"
      >
        <h5>{{tableTitle}}</h5>
        <InputGroup
            v-model="searchTerm"
            placeholder="Search"
            type="text"
            prependIcon="heroicons-outline:search"
            merged
        />
      </div>
      <TableSkeleton v-if="loading" :num-columns="5"></TableSkeleton>
      <vue-good-table v-else
                      :columns="book[currentPage - 1]['columns']"
                      styleClass=" vgt-table bordered centered"
                      :rows="this.book[this.currentPage - 1]['data']"
                      :group-options="{
                        enabled: true,
                        headerPosition: 'bottom',
                      }"
                      :pagination-options="{
                        enabled: true,
                        position: 'top',
                        perPage: 100,
                      }"
                      :search-options="{
                        enabled: true,
                        externalQuery: searchTerm,
                      }"
                      :select-options="{
                        enabled: false,
                        selectOnCheckboxOnly: true, // only select when checkbox is clicked instead of the row
                        // selectioninfoClass: 'custom-class',
                        // selectionText: 'rows selected',
                        // clearSelectionText: 'clear',
                        // disableSelectinfo: true, // disable the select info-500 panel on top
                        // selectAllByGroup: true, // when used in combination with a grouped table, add a checkbox in the header row to check/uncheck the entire group
                      }"
      >
        <template #pagination-top="props">
          <div class="py-4 px-3">
            <Pagination
                :total="book.length"
                :current="currentPage"
                :per-page="perPage"
                :pageRange="pageRange"
                @page-changed="currentPage = $event"
                :pageChanged="props.pageChanged"
                :perPageChanged="props.perPageChanged"
                enableSearch
            >
            </Pagination>
          </div>
        </template>
        <template v-slot:table-row="props">
          <span v-if="props.column.field === 'type'" class="block w-full">
            <span
                class="inline-block px-3 min-w-[90px] text-center mx-auto py-1 rounded-[999px] bg-opacity-25"
                :class="`${
                props.row.type === 'deposit'
                  ? 'text-success-500 bg-success-500'
                  : ''
              }
            ${
              props.row.type === 'exchange'
                ? 'text-warning-500 bg-warning-500'
                : ''
            }
            ${
              props.row.type === 'return'
                ? 'text-danger-500 bg-danger-500'
                : ''
            }

             `"
            >
              {{ props.row.type }}
            </span>
          </span>
          <span v-if="props.column.field == 'actions'">
            <div class="flex space-x-3 rtl:space-x-reverse">
                <Tooltip placement="top" arrow theme="dark" v-for="action in actions">
                  <template #button>
                    <div class="action-btn">
                      <Icon :icon="action.icon" @click="viewContract(props.row.id)"/>
                    </div>
                  </template>
                  <span>{{action.name}}</span>
                </Tooltip>
            </div>
          </span>
        </template>
      </vue-good-table>
    </Card>
  </div>
</template>
<script>
import Dropdown from '@/components/Dropdown';
import Card from '@/components/Card';
import Icon from '@/components/Icon';
import InputGroup from '@/components/InputGroup';
import Pagination from '@/components/Pagination';
import {MenuItem} from '@headlessui/vue';
import Tooltip from '@/components/Tooltip';
import TableSkeleton from '@/components/Skeleton/TableSkeleton.vue';

export default {
  components: {
    Pagination,
    InputGroup,
    Dropdown,
    Icon,
    Card,
    MenuItem,
    Tooltip,
    TableSkeleton,
  },

  props: {
    book: {
      type: Array,
      required: true,
    },
    actions: {
      required: true,
    },
    viewContract: {
      type: Function,
      required: true,
    },
    loading: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    tableTitle() {
      const d = new Date(this.viewDate);
      return 'Deposits on ' + d.toDateString();
    },
    viewDate() {
      return this.loading ? null : this.book[this.currentPage - 1]['date'];
    },
  },
  data() {
    return {
      currentPage: 1,
      perPage: 1,
      pageRange: 5,
      searchTerm: '',
    };
  },
};
</script>
<style lang="scss"></style>
