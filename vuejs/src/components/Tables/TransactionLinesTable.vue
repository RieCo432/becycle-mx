<script>
export default {
  name: 'TransactionLinesTable',
  props: {
    transactionHeader: {
      type: Object,
      required: true,
    },
  },
};
</script>

<template>
  <table class="border-collapse border dark:border-slate-400 min-w-full">
    <thead>
    <tr class=" dark:bg-slate-700">
      <th class="border dark:border-slate-500">Account</th>
      <th class="border dark:border-slate-500">Credit</th>
      <th class="border dark:border-slate-500">Debit</th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="line in transactionHeader.transactionLines" :key="line.id">
      <td class="border dark:border-slate-500">{{line.account.name}}</td>
      <td class="border dark:border-slate-500">{{ line.amount < 0 ? `&#163; ${(-line.amount / 100).toFixed(2)}` : '' }}</td>
      <td class="border dark:border-slate-500">{{ line.amount > 0 ? `&#163; ${(line.amount / 100).toFixed(2)}` : '' }}</td>
    </tr>
    </tbody>
  </table>
</template>

<style scoped lang="scss">

</style>