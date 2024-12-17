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
          <span v-if="props.column.field == 'status'" class="block w-full">
            <span
                class="inline-block px-3 min-w-[90px] text-center mx-auto py-1 rounded-[999px] bg-opacity-25"
                :class="`${
                props.row.status === 'confirmed'
                  ? 'text-success-500 bg-success-500'
                  : ''
              }
            ${
              props.row.status === 'past'
                ? 'text-black-400 bg-black-400'
                : ''
            }
            ${
              props.row.status === 'pending'
                ? 'text-warning-500 bg-warning-500'
                : ''
            }
            ${
              props.row.status === 'cancelled'
                ? 'text-danger-500 bg-danger-500'
                : ''
            }

             `"
            >
              {{ props.row.status }}
            </span>
          </span>
          <span v-if="props.column.field === 'startDateTime'">
            {{ new Date(Date.parse(props.row.startDateTime))
              .toLocaleString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric',
                                           hour: "2-digit", minute: "2-digit", hour12: false, }) }}
          </span>
          <span v-if="props.column.field === 'action'">
            <div class="flex space-x-3 rtl:space-x-reverse">
              <template v-for="action in actions">
                <Tooltip placement="top" arrow theme="dark" :key="action.id"
                         v-if="new Date(Date.parse(props.row.startDateTime)) > new Date() && (isClient || userIsAppointmentManager)">
                  <template #button >
                    <div class="action-btn">
                      <Icon
                          v-if="props.row.status !== 'cancelled' &&
                          !(props.row.status === 'confirmed' && action.id === 'confirm')"
                          :icon="action.icon" @click="action.func(props.row.id)"/>
                    </div>
                  </template>
                  <span>{{action.label}}</span>
                </Tooltip>
              </template>
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
import Card from '@/components/Card';
import Icon from '@/components/Icon';
import InputGroup from '@/components/InputGroup';
import Pagination from '@/components/Pagination';
import Tooltip from '@/components/Tooltip';
import TableSkeleton from '@/components/Skeleton/TableSkeleton.vue';

export default {
  name: 'AppointmentSummaryTable',
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
    cancelAppointment: {
      type: Function,
      required: true,
    },
    editAppointmentNotes: {
      type: Function,
      required: true,
    },
    rescheduleAppointment: {
      type: Function,
      required: true,
    },
    loading: {
      type: Boolean,
      required: true,
    },
    userIsAppointmentManager: {
      type: Boolean,
      required: true,
    },
    isClient: {
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
