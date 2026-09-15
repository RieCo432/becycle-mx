<template>
  <div>
    <Card noborder>
      <div
        class="md:flex justify-between pb-6 md:space-y-0 space-y-3 items-center"
      >
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
          <span
            v-if="props.column.field === 'client'"
            class="text-slate-500 dark:text-slate-300"
          >
            {{ props.row.client.firstName }} {{ props.row.client.lastName }}
          </span>
          <span
            v-if="props.column.field === 'bike'"
            class="text-slate-500 dark:text-slate-300"
          >
            {{ props.row.bike.make }} {{ props.row.bike.model }}
          </span>
          <span
            v-if="props.column.field === 'startDate'"
            class="text-slate-500 dark:text-slate-300"
          >
            {{
              props.row.startDate
                ? new Date(Date.parse(props.row.startDate))
                  .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})
                : 'n/a'
            }}
          </span>
          <span
              v-if="props.column.field === 'endDate'"
              class="text-slate-500 dark:text-slate-300"
          >
            {{
              props.row.endDate
                ? new Date(Date.parse(props.row.endDate))
                  .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})
                : 'n/a'
            }}
          </span>
          <span
              v-if="props.column.field === 'dormantDate'"
              class="text-slate-500 dark:text-slate-300"
          >
            {{
              props.row.dormantDate
                ? new Date(Date.parse(props.row.dormantDate))
                  .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})
                : 'n/a'
            }}
          </span>
          <span
              v-if="props.column.field === 'liability'"
              class="text-slate-500 dark:text-slate-300"
          >
            {{moneyUtils.moneyFormatter(props.row.liability)}}
          </span>

          <div v-if="props.column.field === 'action'" class="flex space-x-3 rtl:space-x-reverse">
            <slot name="action" :contractId="props.row.id"></slot>
          </div>
        </template>
        <template #pagination-bottom="props">
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
      </vue-good-table>
    </Card>
  </div>
</template>
<script>
import Card from '@/components/Card';
import InputGroup from '@/components/InputGroup';
import Pagination from '@/components/Pagination';
import TableSkeleton from '@/components/Skeleton/TableSkeleton.vue';
import moneyUtils from '@/util/moneyUtils';

export default {
  computed: {
    moneyUtils() {
      return moneyUtils;
    },
  },
  components: {
    Pagination,
    InputGroup,
    Card,
    TableSkeleton,
  },

  props: {
    data: {
      required: true,
    },
    columns: {
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
