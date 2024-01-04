<template>
    <div class="grid grid-cols-12 gap-5">
        <div class="lg:col-span-8 col-span-12">
            <Card title="Welcome to beCyCle">
                <p>This is the official website for beCyCle, the community bicycle library and workshop in Aberdeen</p>
            </Card>
        </div>
        <div class="lg:col-span-4 col-span-12">
            <Card title="Opening Times">
                <vue-good-table
                  :columns="columns"
                  :rows="openingTimes"
                  style-class="vgt-table"
                  :sort-options="{
                    enabled: false
                  }"/>
            </Card>
        </div>
    </div>
</template>

<script>
import getOpeningTimes from '@/requests/public';
import Card from '@/components/Card';

export default {
  components: {
    Card,
  },
  data() {
    return {
      columns: [
        {
          label: 'Day',
          field: 'day',
        },
        {
          label: 'Open',
          field: 'open',
        },
        {
          label: 'Close',
          field: 'close',
        },
      ],
    };
  },
  computed: {
    openingTimes: getOpeningTimes(),
  },
};

</script>
<style lang=""></style>
