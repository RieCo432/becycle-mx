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
          <span v-if="props.column.field == 'username'" class="block w-full">
            <span
                class="inline-block px-3 min-w-[90px] text-center mx-auto py-1 rounded-[999px] bg-opacity-25"
                :class="props.row.softDeleted
                  ? 'text-danger-500 bg-danger-500'
                  : 'text-success-500 bg-success-500'"
            >
              {{ props.row.username }}
            </span>
          </span>
          <span v-if="props.column.field === 'admin'" class="flex">
            <Switch
                active-class="bg-primary-500"
                :model-value="props.row.admin"
                @update:modelValue="(eventObj) => patchUser(props.row.id, {admin: eventObj.newValue}, eventObj.failureCallback)"
            />
          </span>
          <span v-if="props.column.field === 'depositBearer'" class="flex">
            <Switch
                active-class="bg-primary-500"
                :model-value="props.row.depositBearer"
                @update:modelValue="(eventObj) => patchUser(props.row.id, {depositBearer: eventObj.newValue}, eventObj.failureCallback)"
            />
          </span>
          <span v-if="props.column.field === 'rentalChecker'" class="flex">
            <Switch
                active-class="bg-primary-500"
                :model-value="props.row.rentalChecker"
                @update:modelValue="(eventObj) => patchUser(props.row.id, {rentalChecker: eventObj.newValue}, eventObj.failureCallback)"
            />
          </span>
          <span v-if="props.column.field === 'appointmentManager'" class="flex">
            <Switch
                active-class="bg-primary-500"
                :model-value="props.row.appointmentManager"
                @update:modelValue="(eventObj) => patchUser(props.row.id, {appointmentManager: eventObj.newValue}, eventObj.failureCallback)"
            />
          </span>
          <span v-if="props.column.field === 'treasurer'" class="flex">
            <Switch
                active-class="bg-primary-500"
                :model-value="props.row.treasurer"
                @update:modelValue="(eventObj) => patchUser(props.row.id, {treasurer: eventObj.newValue}, eventObj.failureCallback)"
            />
          </span>
          <span v-if="props.column.field === 'softDeleted'" class="flex">
            <Switch
                active-class="bg-primary-500"
                :model-value="props.row.softDeleted"
                @update:modelValue="(eventObj) => patchUser(props.row.id, {softDeleted: eventObj.newValue}, eventObj.failureCallback)"
            />
          </span>
          <span v-if="props.column.field == 'action'">
            <div class="flex space-x-3 rtl:space-x-reverse">
                <Tooltip placement="top" arrow theme="dark" v-for="action in actions">
                  <template #button>
                    <div class="action-btn">
                      <Icon :icon="action.icon" @click="patchUser(props.row.id)"/>
                    </div>
                  </template>
                  <span>{{action.name}}</span>
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
  name: 'UserRolesTable',
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
    patchUser: {
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
