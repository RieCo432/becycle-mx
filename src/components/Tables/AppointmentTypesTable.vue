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
        :rows="tableData"
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
          selectAllByGroup: true, // when used in combination with a grouped table, add a checkbox in the header row to check/uncheck the entire group
        }"
      >
        <template v-slot:table-row="props">
          <span v-if="props.column.field === 'active'" class="flex">
            <Switch
                active-class="bg-primary-500"
                :model-value="props.row.active"
                @updateWithCallback="(eventObj) => patchAppointmentType(props.row.id, {active: eventObj.newValue}, eventObj.failureCallback)"
            />
          </span>
          <span v-if="props.column.field == 'actions'">
            <div class="flex space-x-3 rtl:space-x-reverse">
                <Tooltip placement="top" arrow theme="dark" v-for="action in actions">
                  <template #button>
                    <div class="action-btn">
                      <Icon :icon="action.icon" @click="action.func(props.row.id)"/>
                    </div>
                  </template>
                  <span>{{action.label}}</span>
                </Tooltip>
            </div>
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
import Dropdown from '@/components/Dropdown';
import Card from '@/components/Card';
import Icon from '@/components/Icon';
import InputGroup from '@/components/InputGroup';
import Pagination from '@/components/Pagination';
import {MenuItem} from '@headlessui/vue';
import Tooltip from '@/components/Tooltip';
import TableSkeleton from '@/components/Skeleton/TableSkeleton.vue';
import Switch from '@/components/Switch';

export default {
  name: 'AppointmentTypesTable',
  components: {
    Pagination,
    InputGroup,
    Dropdown,
    Icon,
    Card,
    MenuItem,
    Tooltip,
    TableSkeleton,
    Switch,
  },

  props: {
    tableData: {
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
    patchAppointmentType: {
      type: Function,
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
