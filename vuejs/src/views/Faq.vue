<script>
import Card from '@/components/Card';
import Accordion from '@/components/Accordion/index.vue';
import requests from '@/requests';

export default {
  name: 'Faq',
  components: {
    Card,
    Accordion,
  },
  data() {
    return {
      faq: [],
    };
  },
  methods: {
    getFaq() {
      requests.getFaq().then((response) => {
        this.faq = response.data
          .sort((item) => item.orderIndex)
          .map((item) => (
            {
              title: item.question,
              content: item.answer,
            }),
          );
      });
    },
  },
  mounted() {
    this.getFaq();
  },
};
</script>

<template>
  <div class="grid xl:grid-cols-6 grid-cols-1">
    <div class="xl:col-span-4 col-span-1 xl:col-start-2">
      <Card title="Frequently Asked Questions">
        <Accordion :items="faq"></Accordion>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
