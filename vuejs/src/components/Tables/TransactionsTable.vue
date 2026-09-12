<template>
  <div>
    <Card noborder>
      <div
        class="md:flex justify-between pb-6 md:space-y-0 space-y-3 items-center"
      >
        <h5>{{title}}</h5>
      </div>
      <TableSkeleton v-if="loading" :num-columns="columns.length"></TableSkeleton>
      <vue-good-table v-else
        :columns="columns"
        styleClass=" vgt-table bordered centered bg-slate-700"
        :rows="transactions"
        :pagination-options="{
          enabled: false,
          position: 'top'
        }"
        :search-options="{
          enabled: false,
        }"
        :select-options="{
          enabled: false,
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
            <span v-if="props.row.credit > 0">{{ moneyUtils.moneyFormatter(props.row.credit) }}</span>
          </span>
          <span v-if="props.column.field === 'debit'">
            <span v-if="props.row.debit > 0">{{ moneyUtils.moneyFormatter(props.row.debit) }}</span>
          </span>
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
import moneyUtils from '@/util/moneyUtils';

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
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      moneyUtils,
      current: 1,
      perpage: 50,
      pageRange: 5,
      searchTerm: '',
      columns: [
        {
          label: 'Event',
          field: 'event',
        },
        {
          label: 'id',
          field: 'id',
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
