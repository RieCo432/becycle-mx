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
          selectAllByGroup: true,
        }"
      >
        <template v-slot:table-row="props">
          <span v-if="props.column.field === 'username'" class="block w-full">
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
                :disabled="!userIsAdmin"
                active-class="bg-primary-500"
                v-model="props.row.admin"
                @update="(newValue) => patchUser(props.row.id, {admin: newValue})"
            />
          </span>
          <span v-if="props.column.field === 'depositBearer'" class="flex">
            <Switch
                :disabled="!userIsAdmin"
                active-class="bg-primary-500"
                v-model="props.row.depositBearer"
                @update="(newValue) => patchUser(props.row.id, {depositBearer: newValue})"
            />
          </span>
          <span v-if="props.column.field === 'rentalChecker'" class="flex">
            <Switch
                :disabled="!userIsAdmin"
                active-class="bg-primary-500"
                v-model="props.row.rentalChecker"
                @update="(newValue) => patchUser(props.row.id, {rentalChecker: newValue})"
            />
          </span>
          <span v-if="props.column.field === 'appointmentManager'" class="flex">
            <Switch
                :disabled="!userIsAdmin"
                active-class="bg-primary-500"
                v-model="props.row.appointmentManager"
                @update="(newValue) => patchUser(props.row.id, {appointmentManager: newValue})"
            />
          </span>
          <span v-if="props.column.field === 'treasurer'" class="flex">
            <Switch
                :disabled="!userIsAdmin"
                active-class="bg-primary-500"
                v-model="props.row.treasurer"
                @update="(newValue) => patchUser(props.row.id, {treasurer: newValue})"
            />
          </span>
          <span v-if="props.column.field === 'lastAuthenticated' && props.row.lastAuthenticated !== null">
            {{ new Date(Date.parse(props.row.lastAuthenticated))
              .toLocaleString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric',
                hour: "2-digit", minute: "2-digit", hour12: false, }) }}
          </span>
          <span v-if="props.column.field === 'softDeleted'" class="flex">
            <Switch
                :disabled="!userIsAdmin"
                active-class="bg-primary-500"
                v-model="props.row.softDeleted"
                @update="(newValue) => patchUser(props.row.id, {softDeleted: newValue})"
            />
          </span>
            <div v-if="props.column.field === 'actions'" class="flex space-x-3 rtl:space-x-reverse">
                <Tooltip placement="top" arrow theme="dark" v-for="action in actions" :key="action.id">
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
import Switch from '@/components/Switch';

export default {
  name: 'UserRolesTable',
  components: {
    Pagination,
    InputGroup,
    Icon,
    Card,
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
      required: false,
    },
    patchUser: {
      type: Function,
      required: true,
    },
    loading: {
      type: Boolean,
      required: true,
    },
    userIsAdmin: {
      type: Boolean,
      default: false,
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
