<script>
import Card from '@/components/Card/index.vue';
import ComboboxTextInput from '@/components/ComboboxTextInput/ComboboxTextInput.vue';
import requests from '@/requests';
import {debounce} from 'lodash-es';
import Button from '@/components/Button/index.vue';
import Textinput from '@/components/Textinput/index.vue';

export default {
  name: 'findPaperContract',
  components: {Textinput, Button, ComboboxTextInput, Card},
  data() {
    return {
      paperId: null,
      paperIdSuggestions: [],
    };
  },
  methods: {
    fetchPaperIdSuggestions() {
      if (this.paperId != null) {
        requests.getPaperIdSuggestions(this.paperId.toLowerCase()).then((response) => {
          this.paperIdSuggestions = response.data;
        });
      }
    },
    selectPaperId(event, i) {
      this.paperId = this.filteredPaperIdSuggestions[i];
    },
    goToContract() {
      requests.getContractIdFromPaperId(this.paperId).then((response) => {
        this.$router.push({path: `/contracts/${response.data}`});
      });
    },
  },
  created() {
    this.fetchPaperIdSuggestions = debounce(this.fetchPaperIdSuggestions, 500, {leading: true, trailing: true});
  },
  computed: {
    filteredPaperIdSuggestions() {
      return this.paperIdSuggestions.filter((suggestion) => suggestion.startsWith(this.paperId.toLowerCase()));
    },
  },
};
</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <div class="col-span-12 lg:col-span-8">
      <Card title="Find Paper Contract">
        <div class="grid grid-cols-12 gap-5">
          <div class="col-span-12">
            <ComboboxTextInput
              :field-model-value="paperId"
              :suggestions="filteredPaperIdSuggestions"
              :allow-new=false
              :selected-callback="selectPaperId"
            >
              <Textinput
                  label="Paper ID"
                  type="text"
                  placeholder="656...."
                  name="paperId"
                  v-model="paperId"
                  @input="fetchPaperIdSuggestions"
              />
            </ComboboxTextInput>
          </div>
          <div class="col-span-2">
            <Button
                text="Go"
                class="btn-dark"
                @click="goToContract"
            />
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>