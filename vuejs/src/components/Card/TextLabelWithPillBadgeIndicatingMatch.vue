<template>


  <template v-if="dataMatches">
    <Badge
        :label="fieldName"
        badgeClass="bg-opacity-[0.12] pill bg-success-500 text-success-500"
    />
  </template>
  <template v-else>
    <Badge
        :label="fieldName"
        badgeClass="bg-opacity-[0.12] pill bg-danger-500 text-danger-500"
    />
    <Tooltip placement="top" arrow theme="dark">
      <template #button>
        <span class="text-danger-500"><Icon icon="heroicons-outline:information-circle"/></span>
      </template>
      <span>This is not a perfect match.</span>
    </Tooltip>
  </template>
  <slot>
    <span class="block part-text">{{ fieldData }}</span>
  </slot>
</template>
<script>
import Badge from '@/components/Badge/index.vue';
import Tooltip from '@/components/Tooltip/index.vue';
import {string} from 'yup';
import {Icon} from '@iconify/vue';

export default {
  name: 'TextLabelWithPillBadgeIndicatingMatch',
  components: {Icon, Badge, Tooltip},
  props: {
    fieldName: {
      type: string,
      required: true,
    },
    fieldData: {
      required: true,
    },
    searchData: {
      required: true,
    },
  },
  computed: {
    dataMatches() {
      if (this.fieldData === null && this.searchData === null) {
        console.log('null');
        return true;
      } else if (typeof(this.fieldData) === 'string' && typeof(this.searchData) === 'string') {
        console.log('string');
        return this.fieldData.toLowerCase() === this.searchData.toLowerCase();
      } else if (Array.isArray(this.fieldData) && Array.isArray(this.searchData)) {
        console.log('array');
        const allSearchInField = this.searchData.every((sd) => this.fieldData.includes(sd));
        const allFieldInSearch = this.fieldData.every((fd) => this.searchData.includes(fd));
        return allSearchInField && allFieldInSearch;
      }
      return false;
    },
  },
};
</script>
<style scoped lang="scss">
.part-text {
  @apply text-base text-slate-600 dark:text-slate-300 font-medium;
}
</style>