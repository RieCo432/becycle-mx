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
                      :rows="data"
                      :pagination-options="{
                        enabled: true,
                        position: 'top',
                        perPage: perpage,
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
                        // selectAllByGroup: true,
                      }"
                      :sort-options="{
                        enabled: true,
                        initialSortBy: [
                            {field: 'status', type: 'desc'},
                            {field: 'expenseDate', type: 'desc'}
                        ],
                      }">
        <template #pagination-top="props">
          <div class="py-4 px-3">
            <Pagination
                :total="data.length"
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
        <template v-slot:table-row="props">
          <span
              v-if="props.column.field === 'expenseDate'"
              class="text-slate-500 dark:text-slate-300"
          >
            {{ new Date(Date.parse(props.row.expenseDate))
              .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'}) }}
          </span>
          <span
              v-if="props.column.field === 'transferDate'"
              class="text-slate-500 dark:text-slate-300"
          >
            {{ props.row.transferDate ? new Date(Date.parse(props.row.transferDate))
              .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'}) : 'n/a' }}
          </span>
          <span
              v-if="props.column.field === 'amount'"
              class="text-slate-500 dark:text-slate-300"
          >
            &#163; {{ props.row.amount.toFixed(2) }}
          </span>
          <span v-if="props.column.field === 'status'" class="block w-full">
            <span
              class="inline-block px-3 min-w-[90px] text-center mx-auto py-1 rounded-[999px] bg-opacity-25"
              :class="`${
                props.row.status === 'Closed'
                  ? 'text-success-500 bg-success-500'
                  : 'text-danger-500 bg-danger-500'}

             `"
            >
              {{ props.row.status }}
            </span>
          </span>
          <div v-if="props.column.field === 'actions'" class="flex space-x-3 rtl:space-x-reverse">
            <template v-for="action in actions" :key="action.id">
              <template v-if="action.id !== 'markTransferred' || props.row.transferDate === null">
                <Tooltip placement="top" arrow theme="dark">
                  <template #button>
                    <div class="action-btn">
                      <Icon :icon="action.icon" @click="action.func(props.row.id)"/>
                    </div>
                  </template>
                  <span>{{action.label}}</span>
                </Tooltip>
              </template>
            </template>
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
  name: 'ExpenseSummaryTable',
  components: {
    Pagination,
    InputGroup,
    Icon,
    Card,
    Tooltip,
    TableSkeleton,
  },

  props: {
    data: {
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
