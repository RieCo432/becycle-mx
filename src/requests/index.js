import axios from 'axios';
import {useCredentialsStore} from '@/store/credentialsStore';

const credentialsStore = useCredentialsStore();


const axiosClient = axios.create({
  baseURL: 'http://localhost:8000',
});

export default {
  getOpeningTimes() {
    return axiosClient.get('/public/opening-times');
  },
  getUserToken(username, password) {
    return axiosClient.post('/users/token', {
      'username': username,
      'password': password,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  getUserMe() {
    return axiosClient.get('/users/me', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getClientLoginCode(emailAddress) {
    return axiosClient.get('/client/login-code', {
      params: {
        email_address: emailAddress,
      },
    });
  },
  getClientToken(clientId, code) {
    return axiosClient.post('/clients/token', {
      'username': clientId,
      'password': code,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  getClientMe() {
    return axiosClient.get('/clients/me', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getClientByEmail(emailAddress) {
    return axiosClient.get('/clients', {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        email_address: emailAddress,
      },
    });
  },
  postNewClient(clientData) {
    return axiosClient.post('/client', clientData, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getEmailAddressSuggestions(emailAddress) {
    return axiosClient.get('/clients/email-address-suggestions', {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        email_address: emailAddress,
      },
    });
  },
  getClientIdEmailAddress(emailAddress) {
    return axiosClient.get('/client/id-by-email', {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        email_address: emailAddress,
      },
    });
  },
  getBikeMakeSuggestions(make) {
    return axiosClient.get('/bikes/suggest/makes', {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        make: make,
      },
    });
  },
  getBikeModelSuggestions(model) {
    return axiosClient.get('/bikes/suggest/models', {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        model: model,
      },
    });
  },
  getBikeSerialNumberSuggestions(serialNumber) {
    return axiosClient.get('/bikes/suggest/serial-numbers', {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        serial_number: serialNumber,
      },
    });
  },
  getBikeColourSuggestions(colour) {
    return axiosClient.get('/bikes/suggest/colours', {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        colour: colour,
      },
    });
  },
  findBike(make, model, colour, decals, serialNumber) {
    return axiosClient.get('/bike/find', {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        make: make,
        model: model,
        colour: colour,
        decals: decals,
        serial_number: serialNumber,
      },
    });
  },
  getBike(bikeId) {
    return axiosClient.get(`/bikes/${bikeId}`, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  postNewBike(make, model, colour, decals, serialNumber) {
    return axiosClient.post('/bike', {
      make: make,
      model: model,
      colour: colour,
      decals: decals,
      serialNumber: serialNumber,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getContractTypes() {
    return axiosClient.get('/contract/types', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getBikeConditions() {
    return axiosClient.get('/bike/conditions', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getDepositBearers() {
    return axiosClient.get('/users/deposit-bearers', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getActiveUsers() {
    return axiosClient.get('/users/active-users', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getRentalCheckers() {
    return axiosClient.get('/users/rental-checkers', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  checkUserPassword(username, password) {
    return axiosClient.post('/user/check/password', {
      'username': username,
      'password': password,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  checkUserPasswordOrPin(username, password) {
    return axiosClient.post('/user/check/password-or-pin', {
      'username': username,
      'password': password,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  postNewContract(clientId, bikeId, depositAmountCollected, conditionOfBike, contractType, notes, workingUser,
      workingPasswordOrPin, checkingUser, checkingPasswordOrPin, depositCollectingUser, depositCollectingPassword) {
    return axiosClient.post('/contract', {
      contract_data: {
        clientId: clientId,
        bikeId: bikeId,
        depositAmountCollected: depositAmountCollected,
        conditionOfBike: conditionOfBike,
        contractType: contractType,
        notes: notes,
      },
      working_username: workingUser,
      working_user_password_or_pin: workingPasswordOrPin,
      checking_username: checkingUser,
      checking_user_password_or_pin: checkingPasswordOrPin,
      deposit_receiving_username: depositCollectingUser,
      deposit_receiving_user_password: depositCollectingPassword,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  findClient(firstName, lastName, emailAddress) {
    return axiosClient.get('/clients/find', {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        first_name: firstName,
        last_name: lastName,
        email_address: emailAddress,
      },
    });
  },
  getClient(clientId) {
    return axiosClient.get(`/clients/${clientId}`, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getClientContracts(clientId, open, closed, expired) {
    return axiosClient.get(`/clients/${clientId}/contracts`, {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        open: open,
        closed: closed,
        expired: expired,
      },
    });
  },
  getMyContracts(open, closed, expired) {
    return axiosClient.get('/clients/me/contracts', {
      headers: credentialsStore.getApiRequestHeader(),
      params: {
        open: open,
        closed: closed,
        expired: expired,
      },
    });
  },
  getContract(contractId) {
    return axiosClient.get(`/contracts/${contractId}/`, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getUser(userId) {
    return axiosClient.get(`/users/${userId}/`, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchExtendContract(contractId) {
    return axiosClient.patch(`/contracts/${contractId}/extend`, null, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchReturnContract(contractId, depositAmountReturned, depositReturningUser, depositReturningPassword,
      returnAcceptingUser, returnAcceptingPasswordOrPin) {
    return axiosClient.patch(`/contracts/${contractId}/return`, {
      deposit_amount_returned: depositAmountReturned,
      deposit_returning_username: depositReturningUser,
      deposit_returning_user_password: depositReturningPassword,
      working_username: returnAcceptingUser,
      working_user_password_or_pin: returnAcceptingPasswordOrPin,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  postNewTempClient(firstName, lastName, emailAddress) {
    return axiosClient.post('/client/temp', {
      firstName: firstName,
      lastName: lastName,
      emailAddress: emailAddress,
    });
  },
  postTempClientVerificationCode(clientTempId, verificationCode) {
    return axiosClient.post('/client/temp/verify', {
      client_temp_id: clientTempId,
      verification_code: verificationCode,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  getAppointmentTypes() {
    return axiosClient.get('/appointments/types');
  },
  getAvailableAppointmentSlots(appointmentTypeId) {
    return axiosClient.get('/appointments/available', {
      params: {
        appointment_type_id: appointmentTypeId,
      },
    });
  },
  postAppointmentRequest(typeId, startDateTime, notes) {
    return axiosClient.post('/appointments/request', {
      typeId: typeId,
      startDateTime: startDateTime,
      notes: notes,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getMyAppointments(past, future) {
    return axiosClient.get('/clients/me/appointments', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getClientAppointments(clientId, past, future) {
    return axiosClient.get(`/clients/${clientId}/appointments`, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getAppointmentType(typeId) {
    return axiosClient.get(`/appointments/types/${typeId}`);
  },
  getMyContract(contractId) {
    return axiosClient.get(`/clients/me/contracts/${contractId}`, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getOpeningDays() {
    return axiosClient.get('/public/opening-days');
  },
  getOpeningHours() {
    return axiosClient.get('/public/opening-hours');
  },
  getSlotDuration() {
    return axiosClient.get('/public/slot-duration');
  },
  getAppointments(startDate, endDate) {
    return axiosClient.get('/appointments', {
      params: {
        start_datetime: startDate,
        end_datetime: endDate,
      },
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  confirmAppointment(appointmentId) {
    return axiosClient.patch(`/appointments/${appointmentId}/confirm`, {}, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  cancelAppointment(appointmentId) {
    return axiosClient.patch(`/appointments/${appointmentId}/cancel`, {}, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
};
