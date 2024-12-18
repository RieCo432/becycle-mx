<script>
import Card from '@/components/Card/index.vue';

export default {
  name: 'dataPolicy',
  components: {Card},
};
</script>

<template>
    <div class="grid grid-cols-12 gap-5">
        <div class="lg:col-span-6 col-span-12">
            <Card title="Community" class="dark:text-slate-300 text-slate-700">
              <h4 class="dark:text-slate-300 text-slate-700">
                To view the full privacy policy for community members, please click
                  <a href="/community-privacy-policy.html" target="_blank" class="text-blue-500">here</a>.
              </h4>
            </Card>
        </div>
        <div class="lg:col-span-6 col-span-12">
          <Card title="Volunteers">
            <h4 class="dark:text-slate-300 text-slate-700">
              To view the full privacy policy for volunteers, please click
                <a href="/volunteer-privacy-policy.html" target="_blank" class="text-blue-500">here</a>.
            </h4>
          </Card>
        </div>
    </div>
</template>

<style scoped lang="scss">

</style>
