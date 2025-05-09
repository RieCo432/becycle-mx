<script>
import Card from '@/components/Card/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import DashButton from '@/components/Button/index.vue';
import requests from '@/requests';
import {ref} from 'vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import {useToast} from 'vue-toastification';
import Checkbox from '@/components/Switch/index.vue';

const toast = useToast();

export default {
  name: 'ManageFaqCard',
  components: {Card, TextInput, DashButton, Checkbox},
  props: {
    user: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const faqs = ref([]);
    const editFaqId = ref(null);

    const editFaqSchema = yup.object().shape({
      editFaqQuestion: yup.string().required().max(256),
      editFaqAnswer: yup.string().required(),
      editFaqActive: yup.bool(),
    });

    const {handleSubmit: handleEditFaqSubmit} = useForm({
      validationSchema: editFaqSchema,
      keepValuesOnDismount: true,
    });

    const {value: editFaqQuestion, errorMessage: editFaqQuestionError} = useField('editFaqQuestion');
    const {value: editFaqAnswer, errorMessage: editFaqAnswerError} = useField('editFaqAnswer');
    const {value: editFaqActive} = useField('editFaqActive');

    const submitEditFaq = handleEditFaqSubmit(() => {
      if (editFaqId.value) {
        requests.patchFaq(editFaqId.value,
          {
            question: editFaqQuestion.value,
            answer: editFaqAnswer.value,
            active: editFaqActive.value,
          })
          .then((response) => {
            const indexInArray = faqs.value.findIndex((t) => (t.id === editFaqId.value));
            faqs.value.splice(indexInArray, 1, response.data);
            toast.success('FAQ updated', {timeout: 2000});
            editFaqId.value = null;
          })
          .catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 2000});
          });
      }
    });


    const newFaqSchema = yup.object().shape({
      newFaqQuestion: yup.string().required().max(256),
      newFaqAnswer: yup.string().required(),
    });

    const {handleSubmit: handleNewFaqSubmit} = useForm({
      validationSchema: newFaqSchema,
      keepValuesOnDismount: true,
    });

    const {value: newFaqQuestion, errorMessage: newFaqQuestionError, resetField: resetNewQuestion} = useField('newFaqQuestion');
    const {value: newFaqAnswer, errorMessage: newFaqAnswerError, resetField: resetNewAnswer} = useField('newFaqAnswer');

    const submitNewFaq = handleNewFaqSubmit(() => {
      requests.postFaq(
        {
          question: newFaqQuestion.value,
          answer: newFaqAnswer.value,
        })
        .then((response) => {
          faqs.value.push(response.data);
          toast.success('FAQ Added', {timeout: 2000});
          resetNewQuestion();
          resetNewAnswer();
          editFaqId.value = null;
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    });

    return {
      faqs,
      editFaqId,
      editFaqQuestion,
      editFaqQuestionError,
      editFaqAnswer,
      editFaqAnswerError,
      editFaqActive,

      newFaqQuestion,
      newFaqQuestionError,
      newFaqAnswer,
      newFaqAnswerError,

      submitEditFaq,
      submitNewFaq,
    };
  },
  mounted() {
    requests.getAllFaq().then((response) => {
      this.faqs = response.data;
    });
  },
  methods: {
    editFaq(faqId, faqQuestion, faqAnswer, faqActive) {
      this.editFaqId = faqId;
      this.editFaqQuestion = faqQuestion;
      this.editFaqAnswer = faqAnswer;
      this.editFaqActive = faqActive;
    },
    swap(faqIndex1, faqIndex2) {
      const faq1 = this.faqsSorted[faqIndex1];
      const faq2 = this.faqsSorted[faqIndex2];

      requests.swapFaq(faq1.id, faq2.id)
        .then(() => {
          toast.success('FAQ order swapped.', {timeout: 2000});
          const tempOrderIndex = faq1.orderIndex;
          faq1.orderIndex = faq2.orderIndex;
          faq2.orderIndex = tempOrderIndex;
        })
        .catch((error) => {
          toast.error(error.response.data.detail.description, {timeout: 2000});
        });
    },
  },
  computed: {
    faqsSorted: {
      get() {
        return this.faqs.toSorted((itemA, itemB) => itemA.orderIndex - itemB.orderIndex);
      },
    },
  },
};
</script>

<template>
  <Card title="Manage FAQ">
    <form @submit.prevent="submitEditFaq">
      <div class="grid grid-cols-12 gap-2">
        <div class="col-span-4">
          <span class="text-slate-700 dark:text-slate-300 text-xl">Question</span>
        </div>
        <div class="col-span-5">
          <span class="text-slate-700 dark:text-slate-300 text-xl">Answer</span>
        </div>
        <div class="col-span-1">
          <span class="text-slate-700 dark:text-slate-300 text-xl">Active</span>
        </div>
        <div class="col-span-2 grid grid-cols-3">
          <div class="col-span-2">
            <span class="text-slate-700 dark:text-slate-300 text-xl">Order</span>
          </div>
          <div class="col-span-1">
            <span class="text-slate-700 dark:text-slate-300 text-xl">Edit</span>
          </div>
        </div>

        <template v-for="(faq, i) in faqsSorted" :key="faq.id">
          <template v-if="editFaqId == null || editFaqId !== faq.id">
            <div class="col-span-4">
              <span class="text-slate-700 dark:text-slate-300">{{faq.question}}</span>
            </div>
            <div class="col-span-5">
              <span class="text-slate-700 dark:text-slate-300">{{faq.answer}}</span>
            </div>
            <div class="col-span-1">
              <Checkbox
                  name="editFaqActive"
                  disabled
                  v-model="faq.active">
              </Checkbox>
            </div>
            <div class="col-span-2 grid grid-cols-3 gap-x-2">
              <div class="col-span-1">
                <DashButton
                    v-if="i !== faqsSorted.length - 1 && user.appointmentManager"
                    class="btn-sm block-btn"
                    icon="heroicons-outline:arrow-down"
                    @click="() => swap(i, i+1)"/>
              </div>
              <div class="col-span-1">
                <DashButton
                    v-if="i !== 0 && user.appointmentManager"
                    class="btn-sm block-btn"
                    icon="heroicons-outline:arrow-up"
                    @click="() => swap(i, i-1)"/>
              </div>
              <div class="col-span-1">
                <DashButton
                    v-if="user.appointmentManager"
                    :is-disabled="editFaqId != null"
                    @click="editFaq(faq.id, faq.question, faq.answer, faq.active)"
                    class="btn-sm block-btn"
                    icon="heroicons-outline:pencil"/>
              </div>

            </div>


          </template>

          <template v-if="editFaqId === faq.id">
            <div class="col-span-4">
              <TextInput
                  type="text"
                  placeholder="New Question"
                  name="editFaqQuestion"
                  v-model="editFaqQuestion"
                  :error="editFaqQuestionError"
              />
            </div>
            <div class="col-span-5">
              <TextInput
                  type="text"
                  placeholder="New Answer"
                  name="editFaqAnswer"
                  v-model="editFaqAnswer"
                  :error="editFaqAnswerError"
              />
            </div>
            <div class="col-span-1">
              <Checkbox
                  name="editFaqActive"
                  v-model="editFaqActive">
              </Checkbox>
            </div>
            <div class="col-span-2 col-start-11 grid grid-cols-3 gap-x-2">
              <div class="col-span-1 col-start-3">
                <DashButton type="submit" class="btn-sm mx-auto block-btn" icon="heroicons-outline:check"/>
              </div>
            </div>
          </template>
        </template>
      </div>
    </form>
    <form v-if="user.appointmentManager" @submit.prevent="submitNewFaq">
      <div class="grid grid-cols-12 gap-2 mt-2">
        <div class="col-span-4">
          <TextInput
              type="text"
              placeholder="New Question"
              name="newFaqQuestion"
              v-model="newFaqQuestion"
              :error="newFaqQuestionError"
          />
        </div>
        <div class="col-span-6">
          <TextInput
              type="text"
              placeholder="New Answer"
              name="newFaqAnswer"
              v-model="newFaqAnswer"
              :error="newFaqAnswerError"
          />
        </div>
        <div class="col-span-2 col-start-11">
          <DashButton type="submit" class="btn-sm mx-auto block-btn" icon="heroicons-outline:plus"/>
        </div>
      </div>
    </form>
  </Card>
</template>

<style scoped lang="scss">

</style>
