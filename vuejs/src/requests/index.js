import axios from 'axios';
import {useCredentialsStore} from '@/store/credentialsStore';
import router from '@/router';
import {useToast} from 'vue-toastification';


const credentialsStore = useCredentialsStore();
const API_PROTOCOL = import.meta.env.VITE_API_PROTOCOL;
const API_HOST = import.meta.env.VITE_API_HOST;
const API_PORT = import.meta.env.VITE_API_PORT;
const API_SUBDIR = import.meta.env.VITE_API_SUBDIR;
const toast = useToast();


function validateCommonHTTPErrorCodes(status, options) {
  options = options ?? {};
  options.clientLoginRequired = options.clientLoginRequired ?? false;
  options.userLoginRequired = options.userLoginRequired ?? false;
  if (options.clientLoginRequired && status === 401) {
    toast.error('Authentication required. Please log in.', {timeout: 3000});
    credentialsStore.logout();
    router.push('/clients/login');
  } else if (options.userLoginRequired && status === 401) {
    toast.error('Authentication required. Please log in.', {timeout: 3000});
    credentialsStore.logout();
    router.push('/users/login');
  } else if (status === 503) {
    toast.error('Service Temporarily Unavailable. Please try again later.', {timeout: false});
  } else return status < 300;
}

const axiosClient = axios.create({
  baseURL: `${API_PROTOCOL}://${API_HOST}:${API_PORT}${API_SUBDIR}`,
});

export default {
  getOpeningTimes() {
    return axiosClient.get('/public/opening-times');
  },
  getUserToken(username, password) {
    return axiosClient.post('/public/users/token', {
      'username': username,
      'password': password,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getUserMe() {
    return axiosClient.get('/users/me', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getUserMeNo401Redirect() {
    return axiosClient.get('/users/me', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getClientLoginCode(emailAddress) {
    return axiosClient.get('/public/clients/login-code', {
      params: {
        email_address: emailAddress,
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getClientToken(clientId, code) {
    return axiosClient.post('/public/clients/token', {
      'username': clientId,
      'password': code,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getClientMe() {
    return axiosClient.get('/clients/me', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {clientLoginRequired: true}),
    });
  },
  getClientByEmail(emailAddress) {
    return axiosClient.get('/clients', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: {
        email_address: emailAddress,
      },
    });
  },
  postNewClient(clientData) {
    return axiosClient.post('/clients', clientData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getBikeMakeSuggestions(make, maxDistance = 4) {
    return axiosClient.get('/bikes/suggest/makes', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: {
        make: make,
        max_distance: maxDistance,
      },
    });
  },
  getBikeModelSuggestions(model, maxDistance = 4) {
    return axiosClient.get('/bikes/suggest/models', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: {
        model: model,
        max_distance: maxDistance,
      },
    });
  },
  getBikeSerialNumberSuggestions(serialNumber, maxDistance = 4) {
    return axiosClient.get('/bikes/suggest/serial-numbers', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: {
        serial_number: serialNumber,
        max_distance: maxDistance,
      },
    });
  },
  getBikeColourSuggestions(colour, maxDistance = 4) {
    return axiosClient.get('/bikes/suggest/colours', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: {
        colour: colour,
        max_distance: maxDistance,
      },
    });
  },
  getBikeColoursSuggestions(colours, maxDistance = 2) {
    return axiosClient.get('/bikes/suggest/colours', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: {
        colours: colours,
        max_distance: maxDistance,
      },
    });
  },
  findBike(make, model, colours, serialNumber) {
    return axiosClient.get('/bikes/first-match', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: {
        make: make,
        model: model,
        colours: colours,
        serial_number: serialNumber,
      },
    });
  },
  findBikes(make, model, colour, colours, serialNumber, maxDistance = 4) {
    return axiosClient.get('/bikes/find', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: {
        ...(make && {make: make.toLowerCase()}),
        ...(model && {model: model.toLowerCase()}),
        ...(colour && {colour: colour.toLowerCase()}),
        ...(colours && colours.length >= 0 && {colours: colours}),
        ...(serialNumber && {serial_number: serialNumber.toLowerCase()}),
        max_distance: maxDistance,
      },
    });
  },
  getBike(bikeId) {
    return axiosClient.get(`/bikes/${bikeId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getClientBike(bikeId) {
    return axiosClient.get(`/clients/me/bikes/${bikeId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {clientLoginRequired: true}),
    });
  },
  getBikeByRfidTagSerialNumber(rfidTagSerialNumber) {
    return axiosClient.get(`/bikes/tag/${rfidTagSerialNumber}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewBike(make, model, colours, decals, serialNumber) {
    return axiosClient.post('/bikes', {
      make: make,
      model: model,
      colours: colours,
      decals: decals,
      serialNumber: serialNumber,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getContractTypes() {
    return axiosClient.get('/contracts/types', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getBikeConditions() {
    return axiosClient.get('/bikes/conditions', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getDepositBearers() {
    return axiosClient.get('/users/deposit-bearers', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getActiveUsers() {
    return axiosClient.get('/users/active-users', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getRentalCheckers() {
    return axiosClient.get('/users/rental-checkers', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  checkUserPassword(username, password) {
    return axiosClient.post('/users/check/password', {
      'username': username,
      'password': password,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        ...credentialsStore.getApiRequestHeader(),
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  checkUserPasswordOrPin(username, password) {
    return axiosClient.post('/users/check/password-or-pin', {
      'username': username,
      'password': password,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        ...credentialsStore.getApiRequestHeader(),
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  postNewContract(clientId, bikeId, depositAmountCollected, conditionOfBike, contractType, notes, workingUser,
    workingPasswordOrPin, checkingUser, checkingPasswordOrPin, depositCollectingUser, depositCollectingPassword) {
    return axiosClient.post('/contracts', {
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
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getContractDrafts() {
    return axiosClient.get('/contracts/drafts', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getContractDraft(draftContractId) {
    return axiosClient.get(`/contracts/drafts/${draftContractId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewContractDraft() {
    return axiosClient.post('/contracts/drafts', null, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  putDraftContractClient(draftContractId, clientId) {
    return axiosClient.put(`/contracts/drafts/${draftContractId}/client`, {
      client_id: clientId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  putDraftContractBike(draftContractId, bikeId) {
    return axiosClient.put(`/contracts/drafts/${draftContractId}/bike`, {
      bike_id: bikeId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  putDraftContractDetails(draftContractId, contractType, conditionOfBike, notes) {
    return axiosClient.put(`/contracts/drafts/${draftContractId}/details`, {
      conditionOfBike: conditionOfBike,
      contractType: contractType,
      notes: notes,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  putDraftContractDeposit(draftContractId, depositCollectedTransactionHeaderId, depositCollectingUser, depositCollectingPassword) {
    return axiosClient.put(`/contracts/drafts/${draftContractId}/deposit`, {
      deposit_collected_transaction_header_id: depositCollectedTransactionHeaderId,
      deposit_receiving_username: depositCollectingUser,
      deposit_receiving_user_password: depositCollectingPassword,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  putDraftContractWorkingUser(draftContractId, workingUser, workingPasswordOrPin) {
    return axiosClient.put(`/contracts/drafts/${draftContractId}/working-user`, {
      working_username: workingUser,
      working_user_password_or_pin: workingPasswordOrPin,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  putDraftContractCheckingUser(draftContractId, checkingUser, checkingPasswordOrPin) {
    return axiosClient.put(`/contracts/drafts/${draftContractId}/checking-user`, {
      checking_username: checkingUser,
      checking_user_password_or_pin: checkingPasswordOrPin,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postSubmitDraftContract(draftContractId) {
    return axiosClient.post(`/contracts/drafts/${draftContractId}/submit`, null, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  findClient(firstName, lastName, emailAddress, maxDistance = 10) {
    return axiosClient.get('/clients/find', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: {
        first_name: firstName,
        last_name: lastName,
        email_address: emailAddress,
        max_distance: maxDistance,
      },
    });
  },
  getClient(clientId) {
    return axiosClient.get(`/clients/${clientId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getClientContracts(clientId, open, closed, expired) {
    return axiosClient.get(`/clients/${clientId}/contracts`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: {
        open: open,
        closed: closed,
        expired: expired,
      },
    });
  },
  getBikeContracts(bikeId, open, closed, expired) {
    return axiosClient.get(`/bikes/${bikeId}/contracts`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
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
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {clientLoginRequired: true}),
      params: {
        open: open,
        closed: closed,
        expired: expired,
      },
    });
  },
  getContract(contractId) {
    return axiosClient.get(`/contracts/${contractId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getUser(userId) {
    return axiosClient.get(`/users/${userId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchExtendContract(contractId) {
    return axiosClient.patch(`/contracts/${contractId}/extend`, null, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchReturnContract(contractId, depositSettledTransactionHeaderId, depositReturningUser, depositReturningPassword,
    returnAcceptingUser, returnAcceptingPasswordOrPin) {
    return axiosClient.patch(`/contracts/${contractId}/return`, {
      deposit_settled_transaction_header_id: depositSettledTransactionHeaderId,
      deposit_returning_username: depositReturningUser,
      deposit_returning_user_password: depositReturningPassword,
      working_username: returnAcceptingUser,
      working_user_password_or_pin: returnAcceptingPasswordOrPin,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewTempClient(firstName, lastName, emailAddress) {
    return axiosClient.post('/public/clients/temp', {
      firstName: firstName,
      lastName: lastName,
      emailAddress: emailAddress,
    }, {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  postTempClientVerificationCode(clientTempId, verificationCode) {
    return axiosClient.post('/public/clients/temp/verify', {
      client_temp_id: clientTempId,
      verification_code: verificationCode,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getAppointmentTypes(inactive=false) {
    return axiosClient.get('/appointments/types', {
      params: {
        inactive: inactive,
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getAvailableAppointmentSlots(appointmentTypeId, ignoreLimits=undefined) {
    return axiosClient.get('/appointments/available', {
      params: {
        appointment_type_id: appointmentTypeId,
        ...ignoreLimits && {ignore_limits: ignoreLimits},
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  postAppointmentRequest(typeId, startDateTime, notes) {
    return axiosClient.post('/clients/me/appointments/request', {
      typeId: typeId,
      startDateTime: startDateTime,
      notes: notes,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postAppointment(clientId, typeId, startDateTime, notes, ignoreLimits=undefined) {
    return axiosClient.post('/appointments/new', {
      clientId: clientId,
      typeId: typeId,
      startDateTime: startDateTime,
      notes: notes,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      params: ignoreLimits && {ignore_limits: ignoreLimits},
    });
  },
  getMyAppointments(past, future) {
    return axiosClient.get('/clients/me/appointments', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {clientLoginRequired: true}),
    });
  },
  getClientAppointments(clientId, past, future) {
    return axiosClient.get(`/clients/${clientId}/appointments`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getAppointmentType(typeId) {
    return axiosClient.get(`/appointments/types/${typeId}`, {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getMyContract(contractId) {
    return axiosClient.get(`/clients/me/contracts/${contractId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {clientLoginRequired: true}),
    });
  },
  getOpeningDays() {
    return axiosClient.get('/public/opening-days', {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getCalendarTimeRange() {
    return axiosClient.get('/public/calendar-time-range', {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getSlotDuration() {
    return axiosClient.get('/public/slot-duration', {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getAboutUs() {
    return axiosClient.get('/public/about-us', {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getAppointments(startDate, endDate) {
    return axiosClient.get('/appointments/calendar', {
      params: {
        start_datetime: startDate,
        end_datetime: endDate,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  confirmAppointment(appointmentId) {
    return axiosClient.patch(`/appointments/${appointmentId}/confirm`, {}, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  cancelAppointment(appointmentId, data) {
    return axiosClient.patch(`/appointments/${appointmentId}/cancel`, data, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getDepositBook() {
    return axiosClient.get('/finances/deposit-book', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getDepositBalances(onlyAssetAccounts=true) {
    return axiosClient.get('/finances/deposit-accounts', {
      params: {
        only_asset_accounts: onlyAssetAccounts,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getUsers() {
    return axiosClient.get('/users', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchUser(userId, patchData) {
    return axiosClient.patch(`/users/${userId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewUser(username, password, pin, admin, depositBearer, rentalChecker, appointmentManager, treasurer) {
    return axiosClient.post('/users', {
      username: username,
      password_cleartext: password,
      pin_cleartext: pin,
      admin: admin,
      depositBearer: depositBearer,
      rentalChecker: rentalChecker,
      appointmentManager: appointmentManager,
      treasurer: treasurer,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchAppointmentType(appointmentTypeId, patchData) {
    return axiosClient.patch(`/appointments/types/${appointmentTypeId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewAppointmentType(newAppointmentTypeData) {
    return axiosClient.post('/appointments/types', newAppointmentTypeData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchAppointmentGeneralSettings(changedAppointmentGeneralSettings) {
    return axiosClient.patch('/settings/appointments/general', changedAppointmentGeneralSettings, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getAppointmentGeneralSettings() {
    return axiosClient.get('/settings/appointments/general', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  deleteClosedDay(closedDayDate) {
    return axiosClient.delete(`/settings/closed-day/${closedDayDate}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postClosedDay(closedDay) {
    return axiosClient.post('/settings/closed-day', closedDay, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getClosedDays(startDate, endDate) {
    return axiosClient.get('/settings/closed-days', {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getAppointmentConcurrencyLimits() {
    return axiosClient.get('/settings/appointments/concurrency', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchAppointmentConcurrencyLimit(weekday, afterTime, patchData) {
    return axiosClient.patch(`/settings/appointments/concurrency/${weekday}/${afterTime}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewAppointmentConcurrencyLimit(newConcurrencyLimitData) {
    return axiosClient.post('/settings/appointments/concurrency', newConcurrencyLimitData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  deleteAppointmentConcurrencyLimit(weekday, afterTime) {
    return axiosClient.delete(`/settings/appointments/concurrency/${weekday}/${afterTime}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  cancelMyAppointment(appointmentId) {
    return axiosClient.patch(`/clients/me/appointments/${appointmentId}/cancel`, null, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {clientLoginRequired: true}),
    });
  },
  postDepositExchange(amount, fromUsername, fromPassword, toUsername, toPassword) {
    return axiosClient.post('/deposit-exchanges', {
      amount: amount,
      deposit_returning_username: fromUsername,
      deposit_returning_user_password: fromPassword,
      deposit_receiving_username: toUsername,
      deposit_receiving_user_password: toPassword,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getPaperIdSuggestions(paperId) {
    return axiosClient.get('/contracts/paper/suggestions', {
      params: {
        old_id: paperId,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getContractIdFromPaperId(paperId) {
    return axiosClient.get('/contracts/paper', {
      params: {
        paper_id: paperId,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getUserLeaderboard() {
    return axiosClient.get('/statistics/users/leaderboard', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getClientLeaderboard() {
    return axiosClient.get('/statistics/clients/leaderboard', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getBikeLeaderboard() {
    return axiosClient.get('/statistics/bikes/leaderboard', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchChangeNames(patchData) {
    return axiosClient.patch('/clients/me', patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToClientLoginIfUnauthorised(status),
    });
  },
  patchClientChangeDetails(clientId, patchData) {
    return axiosClient.patch(`/clients/${clientId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchBikeChangeDetails(bikeId, patchData) {
    return axiosClient.patch(`/bikes/${bikeId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchContractChangeDetails(contractId, patchData) {
    return axiosClient.patch(`/contracts/${contractId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getTotalContractsDateSeries(interval, startDate=null, endDate=null) {
    return axiosClient.get('/statistics/contracts/total', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getActiveContractsDateSeries(interval, gracePeriod, startDate=null, endDate=null) {
    return axiosClient.get('/statistics/contracts/active', {
      params: {
        interval: interval,
        grace_period: gracePeriod,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getNewContractsDateSeries(interval, startDate=null, endDate=null) {
    return axiosClient.get('/statistics/contracts/new', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getReturnedContractsDateSeries(interval, startDate=null, endDate=null) {
    return axiosClient.get('/statistics/contracts/returned', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getBboxGeojson(northBound, eastBound, southBound, westBound) {
    return axiosClient.get('/maps/bbox-road-map', {
      params: {
        north_bound: northBound,
        east_bound: eastBound,
        south_bound: southBound,
        west_bound: westBound,
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getRoadSegmentReportTypes() {
    return axiosClient.get('/maps/report-types', {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  postNewRoadSegmentReport(roadSegmentId, roadSegmentReportTypeId) {
    return axiosClient.post('/maps/road-segment/report', {
      roadSegmentId: roadSegmentId,
      roadSegmentReportTypeId: roadSegmentReportTypeId,
    }, {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  refreshPotentialDuplicateClients() {
    return axiosClient.get('/admin/duplicates/clients/refresh', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getPotentialDuplicateClients() {
    return axiosClient.get('/admin/duplicates/clients', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchIgnorePotentialClientDuplicate(clientDuplicateId) {
    return axiosClient.patch(`/admin/duplicates/clients/${clientDuplicateId}/ignore`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  putResolvePotentialClientDuplicate(clientDuplicateId, keepClientId, discardClientId) {
    return axiosClient.put(`/admin/duplicates/clients/${clientDuplicateId}/resolve`, {
      discard_client_id: discardClientId,
      keep_client_id: keepClientId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  refreshPotentialDuplicateBikes() {
    return axiosClient.get('/admin/duplicates/bikes/refresh', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getPotentialDuplicateBikes() {
    return axiosClient.get('/admin/duplicates/bikes', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchIgnorePotentialBikeDuplicate(bikeDuplicateId) {
    return axiosClient.patch(`/admin/duplicates/bikes/${bikeDuplicateId}/ignore`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  putResolvePotentialBikeDuplicate(bikeDuplicateId, keepBikeId, discardBikeId) {
    return axiosClient.put(`/admin/duplicates/bikes/${bikeDuplicateId}/resolve`, {
      discard_bike_id: discardBikeId,
      keep_bike_id: keepBikeId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  downloadRawDataExcel() {
    return axiosClient.get('/admin/takeout/contracts.xlsx', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      responseType: 'blob',
    });
  },
  downloadRawDataPdf() {
    return axiosClient.get('/admin/takeout/contracts.pdf', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      responseType: 'blob',
    });
  },
  getContracts() {
    return axiosClient.get('/contracts', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  deleteContract(contractId) {
    return axiosClient.delete(`/contracts/${contractId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getAddress() {
    return axiosClient.get('/public/address', {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getFaq() {
    return axiosClient.get('/public/faq', {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getAllFaq() {
    return axiosClient.get('/settings/faq', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  putAddress(newAddress) {
    return axiosClient.put('/settings/address', newAddress, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchAboutUs(newAboutUs) {
    return axiosClient.patch(`/settings/about-us`, {html: newAboutUs}, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchFaq(faqId, updatedFaq) {
    return axiosClient.patch(`/settings/faq/${faqId}`, updatedFaq, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postFaq(newFaq) {
    return axiosClient.post(`/settings/faq`, newFaq, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  swapFaq(faq1Id, faq2Id) {
    return axiosClient.patch('/settings/faq/swap',
      {
        faq1_id: faq1Id,
        faq2_id: faq2Id,
      },
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      },
    );
  },
  getDepositExchangeUsers() {
    return axiosClient.get('/deposit-exchanges/users', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getTotalDepositsDateSeries(interval, startDate, endDate) {
    return axiosClient.get('/finances/deposits/total', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getClaimableDepositsDateSeries(interval, gracePeriod, startDate=null, endDate=null) {
    return axiosClient.get('/finances/deposits/claimable', {
      params: {
        interval: interval,
        grace_period: gracePeriod,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getDepositsCollectedDateSeries(interval, startDate, endDate) {
    return axiosClient.get('/finances/deposits/collected', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getDepositsReturnedDateSeries(interval, startDate, endDate) {
    return axiosClient.get('/finances/deposits/returned', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getDepositFlowDateSeries(interval, startDate, endDate) {
    return axiosClient.get('/finances/deposits/flow', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getContractsStatus(gracePeriod, startDate=null, endDate=null) {
    return axiosClient.get('/statistics/contracts/status', {
      params: {
        grace_period: gracePeriod,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getDepositsStatus(gracePeriod, startDate=null, endDate=null) {
    return axiosClient.get('/finances/deposits/status', {
      params: {
        grace_period: gracePeriod,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getPercentageDepositReturnedAfterMonths(startDate, endDate) {
    return axiosClient.get('/finances/deposits/return-percentage', {
      params: {
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getWorstCaseRequiredDepositFloat() {
    return axiosClient.get('/finances/deposits/required-float/worst-case', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getRealisticRequiredDepositFloat(gracePeriod) {
    return axiosClient.get('/finances/deposits/required-float/realistic', {
      params: {
        grace_period: gracePeriod,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewExpense(amount, type, tagId, notes, expenseDate, receiptFile) {
    return axiosClient.post('/expenses', {
      amount: amount,
      expense_type: type,
      tag_id: tagId,
      notes: notes,
      expense_date: expenseDate,
      receipt_file: receiptFile,
    }, {
      headers: {
        ...credentialsStore.getApiRequestHeader(),
        'Content-Type': 'multipart/form-data',
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewExpenseClaim(expenseTransactionHeaderId, notes, expenseDate, receiptFile) {
    return axiosClient.post('/expenses/claims', {
      expense_claim_transaction_header_id: expenseTransactionHeaderId,
      notes: notes,
      expense_date: expenseDate,
      receipt_file: receiptFile,
    }, {
      headers: {
        ...credentialsStore.getApiRequestHeader(),
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getExpenseTypes() {
    return axiosClient.get('/expenses/types', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getExpenseTags(inactive=false) {
    return axiosClient.get('/expenses/tags', {
      params: {
        inactive: inactive,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getExpenses(filterByTag=null) {
    return axiosClient.get('/expenses', {
      params: filterByTag ? {tag: filterByTag} : null,
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getExpenseClaims() {
    return axiosClient.get('/expenses/claims', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchExpenseTransferred(expenseId) {
    return axiosClient.patch(`/expenses/${expenseId}/transfer`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchExpenseClaimReimbursed(expenseClaimId, reimbursementTransactionHeaderId) {
    return axiosClient.patch(`/expenses/claims/${expenseClaimId}/reimburse`, {
      reimbursement_transaction_header_id: reimbursementTransactionHeaderId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  deleteExpenseClaim(expenseClaimId) {
    return axiosClient.delete(`/expenses/claims/${expenseClaimId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchExpense(expenseId, amount, type, tagId, notes,
    expenseDate, expenseUserId, transferred, treasurerUserId, transferDate) {
    return axiosClient.patch(`/expenses/${expenseId}`, {
      amount: amount,
      type: type,
      tagId: tagId,
      notes: notes,
      expenseDate: expenseDate,
      expenseUserId: expenseUserId,
      transferred: transferred,
      ...transferred && {treasurerUserId: treasurerUserId},
      ...transferred && {transferDate: transferDate},
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  deleteExpense(expenseId) {
    return axiosClient.delete(`/expenses/${expenseId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getExpenseReceipt(expenseId) {
    return axiosClient.get(`/expenses/${expenseId}/receipt`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      responseType: 'blob',
    });
  },
  getExpenseClaimReceipt(expenseClaimId) {
    return axiosClient.get(`/expenses/claims/${expenseClaimId}/receipt`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      responseType: 'blob',
    });
  },
  getActualCashFlow(interval, startDate, endDate, tag) {
    return axiosClient.get('/finances/cashflow/actual', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
        ...(tag && {tag: tag}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getProvisionalCashFlow(interval, startDate, endDate, tag) {
    return axiosClient.get('/finances/cashflow/provisional', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
        ...(tag && {tag: tag}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getTotalCashFlow(interval, startDate, endDate, tag) {
    return axiosClient.get('/finances/cashflow/total', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
        ...(tag && {tag: tag}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getMyPresentationCard() {
    return axiosClient.get('/users/me/presentation-card', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  deleteMyPresentationCard() {
    return axiosClient.delete('/users/me/presentation-card', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getPresentationCardPhoto(presentationCardId) {
    return axiosClient.get(`/public/users/presentation-cards/${presentationCardId}/photo`, {responseType: 'blob'});
  },
  postMyPresentationCardDetails(name, bio, photo) {
    return axiosClient.post('/users/me/presentation-card', {
      name: name,
      bio: bio,
      ...photo ? {photo: photo} : {},
    }, {
      headers: {
        ...credentialsStore.getApiRequestHeader(),
        'Content-Type': 'multipart/form-data',
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getPublicUserPresentationCards() {
    return axiosClient.get('/public/users/presentation-cards', {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  postUserPresentationCardDetails(presentationCardId, name, bio, photo) {
    return axiosClient.post(`/users/presentation-card/${presentationCardId}`, {
      name: name,
      bio: bio,
      ...photo ? {photo: photo} : {},
    }, {
      headers: {
        ...credentialsStore.getApiRequestHeader(),
        'Content-Type': 'multipart/form-data',
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  deleteUserPresentationCardDetails(presentationCardId) {
    return axiosClient.delete(`/users/presentation-card/${presentationCardId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  deleteContractType(contractTypeId) {
    return axiosClient.delete(`/settings/contract-types/${contractTypeId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postContractType(contractTypeId) {
    return axiosClient.post('/settings/contract-types', {
      id: contractTypeId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  deleteExpenseType(expenseTypeId) {
    return axiosClient.delete(`/settings/expense-types/${expenseTypeId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewExpenseType(expenseTypeId, expenseTypeDescription) {
    return axiosClient.post('/settings/expense-types', {
      id: expenseTypeId,
      description: expenseTypeDescription,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchExpenseType(expenseTypeId, expenseTypeDescription) {
    return axiosClient.patch(`/settings/expense-types/${expenseTypeId}`, {
      description: expenseTypeDescription,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewExpenseTag(expenseTagId, expenseTagDescription) {
    return axiosClient.post('/expenses/tags', {
      id: expenseTagId,
      description: expenseTagDescription,
      active: true,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchExpenseTag(expenseTagId, expenseTagDescription, expenseTagActive) {
    return axiosClient.patch(`/expenses/tags/${expenseTagId}`, {
      description: expenseTagDescription,
      active: expenseTagActive,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getUpcomingClosures() {
    return axiosClient.get('/public/upcoming-closures', {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getUpcomingOpenDates() {
    return axiosClient.get('/public/upcoming-open-dates', {
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getAppointmentViaHyperlink(appointmentId, clientId) {
    return axiosClient.get('/appointments', {
      params: {
        appointment_id: appointmentId,
        client_id: clientId,
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  cancelAppointmentViaHyperlink(appointmentId, clientId) {
    return axiosClient.patch('/appointments/cancel', {}, {
      params: {
        appointment_id: appointmentId,
        client_id: clientId,
      },
      validateStatus: (status) => validateCommonHTTPErrorCodes(status),
    });
  },
  getPermissions() {
    return axiosClient.get('/admin/permissions', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  addUserPermission(userId, permissionId) {
    return axiosClient.post(`/users/${userId}/permissions`, {permissionId: permissionId},
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      });
  },
  removeUserPermission(userId, permissionId) {
    return axiosClient.delete(`/users/${userId}/permissions/${permissionId}`,
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      },
    );
  },
  addGroupPermission(groupId, permissionId) {
    return axiosClient.post(`/groups/${groupId}/permissions`, {permissionId: permissionId},
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      });
  },
  removeGroupPermission(groupId, permissionId) {
    return axiosClient.delete(`/groups/${groupId}/permissions/${permissionId}`,
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      },
    );
  },
  addGroupUser(groupId, userId) {
    return axiosClient.post(`/groups/${groupId}/users`, {user_id: userId},
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      });
  },
  removeGroupUser(groupId, userId) {
    return axiosClient.delete(`/groups/${groupId}/users/${userId}`,
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      },
    );
  },
  getUserPermissions(userId) {
    return axiosClient.get(`/users/${userId}/permissions`,
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      },
    );
  },
  getGroupPermissions(groupId) {
    return axiosClient.get(`/groups/${groupId}/permissions`,
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      },
    );
  },
  getUserGroups() {
    return axiosClient.get('/groups',
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      },
    );
  },
  postUserGroup(name) {
    return axiosClient.post('/groups', {name: name},
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      },
    );
  },
  deleteUserGroup(groupId) {
    return axiosClient.delete(`/groups/${groupId}`,
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      });
  },
  getGroupUsers(groupId) {
    return axiosClient.get(`/groups/${groupId}/users`,
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      },
    );
  },
  postCrimeReport(data) {
    return axiosClient.post('/crimereports', data, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  patchCloseCrimeReport(crimeReportId) {
    return axiosClient.patch(`/crimereports/${crimeReportId}/close`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  findCrimeReport(crimeNumber) {
    return axiosClient.get('/crimereports/find', {
      params: {
        crime_number: crimeNumber,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  swapAppointmentTypes(type1Id, type2Id) {
    return axiosClient.patch('/settings/appointments/swap',
      {
        appointment_type_1_id: type1Id,
        appointment_type_2_id: type2Id,
      },
      {
        headers: credentialsStore.getApiRequestHeader(),
        validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
      },
    );
  },
  getColours() {
    return axiosClient.get('/colours', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getAccounts(queryParams=undefined) {
    return axiosClient.get(`/accounts${
      queryParams ?
        `?${queryParams.map((p) => `${encodeURIComponent(p.name)}=${encodeURIComponent(p.value)}`).join('&')}` :
        ''
    }`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  postNewAccount(name, description, type, owneruserId, ownerGroupId, scheduledClosureDate, isInternal, showInUis, restrictedToProjectId) {
    return axiosClient.post('/accounts', {
      name: name,
      description: description,
      type: type,
      ownerUserId: owneruserId,
      ownerGroupId: ownerGroupId,
      scheduledClosureDate: scheduledClosureDate,
      isInternal: isInternal,
      showInUis: showInUis,
      restrictedToProjectId: restrictedToProjectId,
    },
    {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  putUpdateAccount(accountId, name, description, scheduledClosureDate, showInUis) {
    return axiosClient.put(`/accounts/${accountId}`, {
      name: name,
      description: description,
      scheduledClosureDate: scheduledClosureDate,
      showInUis: showInUis,
    },
    {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  closeAccount(accountId) {
    return axiosClient.patch(`/accounts/${accountId}/close`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  reopenAccount(accountId) {
    return axiosClient.patch(`/accounts/${accountId}/reopen`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getFormattedTransactionHeaders() {
    return axiosClient.get('/transactions/formatted', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  createTransaction(transaction) {
    return axiosClient.post('/transactions', transaction, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
  getProjects() {
    return axiosClient.get('/settings/projects', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => validateCommonHTTPErrorCodes(status, {userLoginRequired: true}),
    });
  },
};
