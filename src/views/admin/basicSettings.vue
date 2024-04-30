<script>
import Card from '@/components/Card/index.vue';
import * as yup from 'yup';
import {useField, useForm} from 'vee-validate';
import requests from '@/requests';
import Button from '@/components/Button/index.vue';
import Textinput from '@/components/Textinput/index.vue';
import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  name: 'basicSettings',
  components: {Textinput, Button, Card},
  setup() {
    const newAddressSchema = yup.object().shape({
      number: yup.string().required('Street Number is required'),
      street: yup.string().required('Street Name is required'),
      postcode: yup.string().required('Postcode is required'),
      city: yup.string().required('City is required'),
    });

    const {handleSubmit} = useForm({
      validationSchema: newAddressSchema,
      keepValuesOnUnmount: true,
    });

    const {value: number, errorMessage: numberError} = useField('number');
    const {value: street, errorMessage: streetError} = useField('street');
    const {value: postcode, errorMessage: postcodeError} = useField('postcode');
    const {value: city, errorMessage: cityError} = useField('city');

    const submitChangeDetails = handleSubmit(() => {
      requests.putAddress(
          {
            number: number.value,
            street: street.value,
            postcode: postcode.value,
            city: city.value,
          }).then((response) => {
        toast.success('Address updated', {timeout: 2000});
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    });

    return {
      number,
      numberError,
      street,
      streetError,
      postcode,
      postcodeError,
      city,
      cityError,
      submitChangeDetails,
    };
  },
  data() {
    return {
      address: null,
    };
  },
  mounted() {
    requests.getAddress().then((response) => {
      this.address = response.data;
      this.number = this.address.number;
      this.street = this.address.street;
      this.postcode = this.address.postcode;
      this.city = this.address.city;
    });
  },
};
</script>

<template>
  <div class="grid grid-cols-3">
    <Card title="Update Address">
      <form @submit.prevent="submitChangeDetails">
        <div class="grid grid-cols-12 gap-5">
          <div class="md:col-span-6 col-span-12">
            <Textinput
                label="Street Number"
                type="text"
                placeholder="21-23"
                name="number"
                v-model="number"
                :error="numberError"
            />
          </div>
          <div class="md:col-span-6 col-span-12">
            <Textinput
                label="Street Name"
                type="text"
                placeholder="High Street"
                name="street"
                v-model="street"
                :error="streetErrort"
            />
          </div>
          <div class="col-span-6">
            <Textinput
                label="Post Code"
                type="text"
                placeholder="AB24 3EE"
                name="postcode"
                v-model="postcode"
                :error="postcodeError"
            />
          </div>
          <div class="col-span-6">
            <Textinput
                label="City"
                type="text"
                placeholder="Aberdeen"
                name="city"
                v-model="city"
                :error="cityError"
            />
          </div>
          <div class="col-span-12">
            <Button type="submit" class="btn btn-dark block w-full text-center">
              Submit
            </Button>
          </div>
        </div>
      </form>
    </Card>
  </div>
</template>

<style scoped lang="scss">

</style>