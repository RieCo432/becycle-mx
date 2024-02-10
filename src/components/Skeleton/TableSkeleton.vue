<template>
  <div class="w-full bg-white dark:bg-slate-700 shadow-base p-6 rounded-md">
    <table
      class="animate-pulse w-full border-separate border-spacing-4 table-fixed"
    >
      <thead>
        <tr>
          <th scope="col" v-for="(column, i) in columns" :key="i">
            <div class="h-4 bg-[#C4C4C4] dark:bg-slate-500"></div>
          </th>
        </tr>
      </thead>
      <tbody class="table-group-divider">
        <tr v-for="(item, i) in items" :key="i">
          <td v-for="(column, j) in columns" :key="j">
            <div class="h-2 bg-[#C4C4C4] dark:bg-slate-500"></div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script>
export default {
  name: 'TableSkeleton',
  props: {
    count: {
      type: Number,
      default: 6,
    },
    numColumns: {
      type: Number,
      required: true,
    },
  },

  computed: {
    items() {
      return Array.from({length: this.count});
    },
    columns() {
      return Array.from({length: this.numColumns});
    },
  },
};
</script>
<style lang=""></style>
