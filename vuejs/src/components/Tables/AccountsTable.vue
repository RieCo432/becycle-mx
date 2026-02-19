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
      <TableSkeleton v-if="accounts === null" :num-columns="columns.length"></TableSkeleton>
      <vue-good-table v-else
        :columns="columns"
        styleClass=" vgt-table bordered centered"
        :rows="accounts.sort(accountsSorting)"
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
              &#163;{{ (props.row.normalisedBalance / 100).toFixed(2) }}
            </span>
          </span>
          <span v-if="props.column.field === 'isInternal'">
            <Icon v-if="props.row.isInternal" icon="heroicons-outline:check"/>
            <Icon v-else icon="heroicons-outline:x-mark"/>
          </span>
          <span v-if="props.column.field === 'closedOn' && props.row.closedOn !== null">
            {{ new Date(Date.parse(props.row.closedOn))
              .toLocaleString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric',
                hour: "2-digit", minute: "2-digit", hour12: false, }) }}
          </span>
          <span v-if="props.column.field === 'showInUis'">
            {{ props.row.showInUis.join(', ') }}
          </span>
            <div v-if="props.column.field === 'actions'" class="flex space-x-3 rtl:space-x-reverse">
                <Tooltip
                        placement="top"
                        arrow
                        theme="dark"
                        v-for="action in actions.filter((a) => a.showIf(props.row))"
                        :key="action.id">
                  <template #button>
                    <div class="action-btn">
                      <Icon :icon="action.icon" @click="action.func(props.row.id)"/>
                    </div>
                  </template>
                  <span>{{action.label}}</span>
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
  name: 'AccountsTable',
  components: {
    Pagination,
    InputGroup,
    Icon,
    Card,
    Tooltip,
    TableSkeleton,
  },

  props: {
    accounts: {
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
  emits: ['close-account', 'reopen-account'],
  methods: {
    accountsSorting(a, b) {
      const isAClosed = !!a.closedOn;
      const isBClosed = !!b.closedOn;
      if (isAClosed && !isBClosed) {
        return 1;
      }
      if (!isAClosed && isBClosed) {
        return -1;
      }
      if (isAClosed && isBClosed) {
        return b.closedOn.localeCompare(a.closedOn);
      }
      return a.name.localeCompare(b.name);
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
          label: 'Name',
          field: 'name',
        },
        {
          label: 'Description',
          field: 'description',
        },
        {
          label: 'Balance',
          field: 'normalisedBalance',
        },
        {
          label: 'Type',
          field: 'type',
        },
        {
          label: 'Internal?',
          field: 'isInternal',
        },
        {
          label: 'Owner User',
          field: 'ownerUser.username',
        },
        {
          label: 'Owner Group',
          field: 'ownerGroup.name',
        },
        {
          label: 'Scheduled Closure Date',
          field: 'scheduledClosureDate',
        },
        {
          label: 'Closed On',
          field: 'closedOn',
        },
        {
          label: 'Closed By',
          field: 'closedByUser.username',
        },
        {
          label: 'Show in UI',
          field: 'showInUis',
        },
        {
          label: 'Actions',
          field: 'actions',
          sortable: false,
        },
      ],
      actions: [
        {
          label: 'Close Account',
          icon: 'heroicons-outline:lock-closed',
          id: 1,
          func: (id) => this.$emit('close-account', id),
          showIf: (row) => !row.closedOn,
        },
        {
          label: 'Reopen Account',
          icon: 'heroicons-outline:lock-open',
          id: 2,
          func: (id) => this.$emit('reopen-account', id),
          showIf: (row) => row.closedOn,
        },
      ],
    };
  },
};
</script>
<style lang="scss"></style>
