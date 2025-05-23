<template>
  <div>
    <Card noborder>
      <div
        class="md:flex justify-between pb-6 md:space-y-0 space-y-3 items-center"
      >
        <h5>{{title}}</h5>
        <InputGroup
          v-model="searchTerm"
          placeholder="Search"
          type="text"
          prependIcon="heroicons-outline:search"
          merged
        />
      </div>
      <TableSkeleton v-if="loading" :num-columns="columns.length"></TableSkeleton>
      <vue-good-table v-else
        :columns="columns"
        styleClass=" vgt-table bordered centered"
        :rows="advancedTable"
        :pagination-options="{
          enabled: false,
          perPage: perpage,
        }"
        :search-options="{
          enabled: true,
          externalQuery: searchTerm,
        }"
        :select-options="{
          enabled: false,
          selectOnCheckboxOnly: true, // only select when checkbox is clicked instead of the row
          selectioninfoClass: 'custom-class',
          selectionText: 'rows selected',
          clearSelectionText: 'clear',
          disableSelectinfo: true, // disable the select info-500 panel on top
          selectAllByGroup: true,
        }"
      >
        <template v-slot:table-row="props">
          <span v-if="props.column.field === 'customer'" class="flex">
            <span class="w-7 h-7 rounded-full ltr:mr-3 rtl:ml-3 flex-none">
              <img
                :src="props.row.customer.image"
                :alt="props.row.customer.name"
                class="object-cover w-full h-full rounded-full"
              />
            </span>
            <span
              class="text-sm text-slate-600 dark:text-slate-300 capitalize"
              >{{ props.row.customer.name }}</span
            >
          </span>
          <span
            v-if="props.column.field === 'startDate'"
            class="text-slate-500 dark:text-slate-300"
          >
            {{ new Date(Date.parse(props.row.startDate))
              .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'}) }}
          </span>
          <span
              v-if="props.column.field === 'endDate'"
              class="text-slate-500 dark:text-slate-300"
          >
            {{ new Date(Date.parse(props.row.endDate))
              .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'}) }}
          </span>
          <span
              v-if="props.column.field === 'returnedDate'"
              class="text-slate-500 dark:text-slate-300"
          >
            {{ props.row.returnedDate ? new Date(Date.parse(props.row.returnedDate))
              .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'}) : 'n/a' }}
          </span>
          <span v-if="props.column.field === 'status'" class="block w-full">
            <span
              class="inline-block px-3 min-w-[90px] text-center mx-auto py-1 rounded-[999px] bg-opacity-25"
              :class="`${
                props.row.status === 'closed'
                  ? 'text-success-500 bg-success-500'
                  : ''
              }
            ${
              props.row.status === 'open'
                ? 'text-warning-500 bg-warning-500'
                : ''
            }
            ${
              props.row.status === 'expired'
                ? 'text-danger-500 bg-danger-500'
                : ''
            }

             `"
            >
              {{ props.row.status }}
            </span>
          </span>
          <div v-if="props.column.field === 'action'" class="flex space-x-3 rtl:space-x-reverse">
            <Tooltip placement="top" arrow theme="dark" v-for="action in actions" :key="action.id">
              <template #button>
                <div class="action-btn">
                  <Icon :icon="action.icon" @click="viewContract(props.row.id)"/>
                </div>
              </template>
              <span>{{action.name}}</span>
            </Tooltip>
          </div>
        </template>
        <template #pagination-bottom="props">
          <div class="py-4 px-3">
            <Pagination
              :total="advancedTable.length"
              :current="current"
              :per-page="perpage"
              :pageRange="pageRange"
              @page-changed="current = $event"
              :pageChanged="props.pageChanged"
              :perPageChanged="props.perPageChanged"
              enableSearch>
            </Pagination>
          </div>
        </template>
      </vue-good-table>
    </Card>
  </div>
</template>
<script>
import Card from '@/components/Card';
import Icon from '@/components/Icon';
import InputGroup from '@/components/InputGroup';
import Pagination from '@/components/Pagination';
import Tooltip from '@/components/Tooltip';
import TableSkeleton from '@/components/Skeleton/TableSkeleton.vue';

export default {
  components: {
    Pagination,
    InputGroup,
    Icon,
    Card,
    Tooltip,
    TableSkeleton,
  },

  props: {
    advancedTable: {
      required: true,
    },
    columns: {
      required: true,
    },
    actions: {
      required: true,
    },
    title: {
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
  data() {
    return {
      current: 1,
      perpage: 10,
      pageRange: 5,
      searchTerm: '',
    };
  },
};
</script>
<style lang="scss"></style>
