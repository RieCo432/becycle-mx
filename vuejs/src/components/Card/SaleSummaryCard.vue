<script>
import Card from '@/components/Card/index.vue';
import Tooltip from '@/components/Tooltip/index.vue';
import TextLabelWithPillBadgeIndicatingMatch from '@/components/Card/TextLabelWithPillBadgeIndicatingMatch.vue';
import Button from '@/components/Button/index.vue';
import {number} from 'yup';

export default {
  name: 'SaleSummaryCard',
  methods: {number},
  components: {Button, TextLabelWithPillBadgeIndicatingMatch, Tooltip, Card},
  props: {
    saleHeader: {
      type: Object,
      required: true,
    },
  },
  computed: {
    numberOfItemSaleLines() {
      return this.saleHeader.catalogueItemSaleLines.length;
    },
    numberOfBikeSaleLines() {
      return this.saleHeader.bikeSaleLines.length;
    },
    maximumNumberOfSaleLines() {
      return Math.max(this.numberOfBikeSaleLines, this.numberOfItemSaleLines);
    },
  },
};
</script>

<template>
  <Card
      :title="saleHeader.transactionHeaderId ?
      `Closed By ${saleHeader.transactionHeader?.postedByUser.username} @ ${new Date(Date.parse(saleHeader.transactionHeader.postedOn))
              .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})}` :
              `Started By ${saleHeader.createdByUser.username} @ ${new Date(Date.parse(saleHeader.createdOn))
              .toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'})}`"
      class-name="border border-solid dark:border-slate-600 border-l-2 border-t-2 shadow-lg dark:shadow-slate-900 h-full">
    <div class="grid h-full gap-5" :class="saleHeader.transactionHeaderId == null ? 'grid-cols-2' : 'grid-cols-3'">
      <div class="col-span-2">
        <div class="flex flex-col">
          <div class="w-full flex-shrink">
            <div class="grid grid-cols-11 gap-2 divide-x divide-y dark:text-slate-300 text-slate-700 align-middle">
              <div class="col-span-full text-center"><h4>Sale Content</h4></div>

              <div class="col-span-5 grid grid-cols-5 gap-2 divide-x divide-y dark:text-slate-300 text-slate-700 align-middle">
                <div class="col-span-5 text-center h-10"><h4>Catalogue Items</h4></div>
                <div class="col-span-3 text-left h-8"><h6>Item</h6></div>
                <div class="col-span-1 text-right h-8"><h6>Qty</h6></div>
                <div class="col-span-1 text-right h-8"><h6>Price</h6></div>
                <template v-for="line in saleHeader.catalogueItemSaleLines" :key="line.id">
                  <div class="col-span-3 h-8"><span>{{ line.catalogueItem.name }}</span></div>
                  <div class="col-span-1 text-right h-8">
                    <span class="inline align-bottom mb-0">{{ line.quantity }}</span>
                  </div>
                  <div class="col-span-1 text-right h-8">
                    <span class="inline align-bottom mb-0">{{ (line.salePrice / 100).toFixed(2) }}</span>
                  </div>
                </template>
                <div class="col-span-full h-8" v-for="i in (maximumNumberOfSaleLines - numberOfItemSaleLines + 1)" :key="i"></div>
                <div class="col-span-4 text-center h-8"><h5>Sub Total</h5></div>
                <div class="col-span-1 text-right h-8"><h5>{{ (saleHeader.catalogueItemSaleLines.reduce((total, line) => total + line.salePrice, 0) / 100).toFixed(2) }}</h5></div>
              </div>
              <div class="col-span-1"></div>

              <div class="col-span-5 grid grid-cols-5 gap-2 divide-x divide-y dark:text-slate-300 text-slate-700 align-middle">
                <div class="col-span-5 text-center h-10"><h4>Bikes</h4></div>
                <div class="col-span-1 text-left h-8"><h6>Make</h6></div>
                <div class="col-span-1 left h-8"><h6>Model</h6></div>
                <div class="col-span-1 text-left h-8"><h6>Colours</h6></div>
                <div class="col-span-1 text-left h-8"><h6>Serial No.</h6></div>
                <div class="col-span-1 text-right h-8"><h6>Price</h6></div>
                <template v-for="line in saleHeader.bikeSaleLines" :key="line.id">
                  <div class="col-span-1 h-8"><span>{{ line.bike.make }}</span></div>
                  <div class="col-span-1 h-8"><span>{{ line.bike.model }}</span></div>
                  <div class="col-span-1 h-8">
                    <div class="h-full rounded-full overflow-hidden">
                      <div :class="`w-full h-full rounded-full overflow-hidden grid grid-cols-${line.bike.colours.length}`">
                        <template
                          v-for="c in line.bike.colours"
                          :key="c.name"
                        >
                          <Tooltip placement="top" arrow theme="dark" btn-class="col-span-1" :btn-style="{backgroundColor: c.hex}">
                            <template #button>
                              <div class="w-full h-full"></div>
                            </template>
                            <span>{{ c.name }} ({{ c.hex }})</span>
                          </Tooltip>
                        </template>
                      </div>
                    </div>
                  </div>
                  <div class="col-span-1 text-left h-8"><span>{{ line.bike.serialNumber }}</span></div>
                  <div class="col-span-1 text-right h-8">
                    <span class="inline align-bottom mb-0">{{ (line.salePrice / 100).toFixed(2) }}</span>
                  </div>
                </template>
                <div class="col-span-full h-8" v-for="i in (maximumNumberOfSaleLines - numberOfBikeSaleLines + 1)" :key="i"></div>
                <div class="col-span-4 text-center h-8"><h5>Sub Total</h5></div>
                <div class="col-span-1 text-right h-8"><h5>{{ (saleHeader.bikeSaleLines.reduce((total, line) => total + line.salePrice, 0) / 100).toFixed(2) }}</h5></div>
                
              </div>
              <div class="col-span-full h-8"></div>
              <div class="col-span-9 col-start-1 text-center h-8"><h5>Total</h5></div>
              <div class="col-span-2 col-start-10 text-right h-8"><h5>{{ ((saleHeader.catalogueItemSaleLines.reduce((total, line) => total + line.salePrice, 0) + saleHeader.bikeSaleLines.reduce((total, line) => total + line.salePrice, 0)) / 100).toFixed(2) }}</h5></div>
            </div>
          </div>
        </div>
        
        
        <div class="col-span-1">
          <div class="flex flex-col">
            <div class="w-full flex-shrink">
              <div class="grid grid-cols-10 gap-2 divide-x divide-y dark:text-slate-300 text-slate-700 align-middle">
                
                
                <div class="col-span-full h-10"></div>
                
              </div>
            </div>
          </div>
        </div>
        <div class="col-span-2"></div>
      </div>
      
      <div v-if="saleHeader.transactionHeaderId != null"  class="col-span-1 flex flex-col">
        <div class="flex flex-col justify-center items-center mb-2">
          <h4>Payment Transaction</h4>
        </div>
        <div class="flex flex-col">
          <table
            class="border-collapse border dark:border-slate-400 min-w-full text-slate-600 dark:text-slate-300">
            <tr class=" dark:bg-slate-700">
              <th class="border dark:border-slate-500">Account</th>
              <th class="border dark:border-slate-500">Credit</th>
              <th class="border dark:border-slate-500">Debit</th>
            </tr>
            <tr v-for="line in saleHeader.transactionHeader.transactionLines" :key="line.id">
              <td class="border dark:border-slate-500">{{ line.account.name }}</td>
              <td class="border dark:border-slate-500">
                {{ line.amount < 0 ? `&#163; ${(-line.amount / 100).toFixed(2)}` : '' }}
              </td>
              <td class="border dark:border-slate-500">
                {{ line.amount > 0 ? `&#163; ${(line.amount / 100).toFixed(2)}` : '' }}
              </td>
            </tr>
          </table>
        </div>
      </div>
      <div class="col-span-full">
        <slot name="footer"/>
      </div>
    </div>
  </Card>
</template>

<style scoped lang="scss">
.part-label {
  @apply text-base text-slate-400 dark:text-slate-400 mb-1;
}
.part-text {
  @apply text-base text-slate-600 dark:text-slate-300 font-medium;
}
</style>
