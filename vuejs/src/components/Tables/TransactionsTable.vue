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
      <TableSkeleton v-if="transactions === null" :num-columns="columns.length"></TableSkeleton>
      <vue-good-table v-else
        :columns="columns"
        styleClass=" vgt-table bordered centered bg-slate-700"
        :rows="transactions.sort(transactionSorting)"
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
        :group-options="{
          enabled: true,
          headerPosition: 'top',
          collapsable: true,
        }"
      >
        <template v-slot:table-header-row="props">
          <span v-if="props.column.field === 'createdOn' && props.row.createdOn !== null">
            {{ new Date(Date.parse(props.row.createdOn))
            .toLocaleString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric',
              hour: "2-digit", minute: "2-digit", hour12: false, }) }}
          </span>
          <span v-if="props.column.field === 'postedOn' && props.row.postedOn !== null">
            {{ new Date(Date.parse(props.row.postedOn))
            .toLocaleString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric',
              hour: "2-digit", minute: "2-digit", hour12: false, }) }}
          </span>
        </template>
        <template v-slot:table-row="props">
          <span v-if="props.column.field === 'username'" class="block w-full">
            <span
                class="inline-block px-3 min-w-[90px] text-center mx-auto py-1 rounded-[999px] bg-opacity-25"
                :class="props.row.closedOn === null
                  ? 'text-danger-500 bg-danger-500'
                  : 'text-success-500 bg-success-500'">
              {{ props.row.name }}
            </span>
          </span>
          <span v-if="props.column.field === 'normalisedBalance'">
            <span
              class="inline-block px-3 min-w-[90px] text-center mx-auto py-1 rounded-[999px] bg-opacity-25"
              :class="props.row.normalisedBalance < 0
                  ? 'text-danger-500 bg-danger-500'
                  : 'text-success-500 bg-success-500'">
              {{ props.row.normalisedBalance }}
            </span>
          </span>
          <span v-if="props.column.field === 'isInternal'">
            <Icon v-if="props.row.isInternal" icon="heroicons-outline:check"/>
            <Icon v-else icon="heroicons-outline:x-mark"/>
          </span>
          <span v-if="props.column.field === 'credit'">
            <span v-if="props.row.credit > 0">{{props.row.credit}}</span>
          </span>
          <span v-if="props.column.field === 'debit'">
            <span v-if="props.row.debit > 0">{{props.row.debit}}</span>
          </span>
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
  name: 'TransactionsTable',
  components: {
    Pagination,
    InputGroup,
    Icon,
    Card,
    Tooltip,
    TableSkeleton,
  },

  props: {
    transactions: {
      required: true,
      type: Array,
    },
    title: {
      required: false,
    },
    userIsAdmin: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    transactionSorting(a, b) {
      return b.createdOn.localeCompare(a.createdOn);
    },
  },
  data() {
    return {
      current: 1,
      perpage: 10,
      pageRange: 5,
      searchTerm: '',
      columns: [
        {
          label: 'Event',
          field: 'event',
        },
        {
          label: 'Created On',
          field: 'createdOn',
        },
        {
          label: 'Created By',
          field: 'createdByUsername',
        },
        {
          label: 'Posted On',
          field: 'postedOn',
        },
        {
          label: 'Posted By',
          field: 'postedByUsername',
        },
        {
          label: 'Account',
          field: 'accountName',
        },
        {
          label: 'Credit',
          field: 'credit',
        },
        {
          label: 'Debit',
          field: 'debit',
        },
      ],
      actions: [],
    };
  },
};
</script>
<style lang="scss">
</style>
