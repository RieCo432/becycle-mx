import axios from 'axios';
import {useCredentialsStore} from '@/store/credentialsStore';
import router from '@/router';


const credentialsStore = useCredentialsStore();
const API_PROTOCOL = import.meta.env.VITE_API_PROTOCOL;
const API_HOST = import.meta.env.VITE_API_HOST;
const API_PORT = import.meta.env.VITE_API_PORT;
const API_SUBDIR = import.meta.env.VITE_API_SUBDIR;

function redirectToUserLoginIfUnauthorised(status) {
  if (status === 401) {
    credentialsStore.logout();
    router.push('/users/login');
  } else return status < 300;
}


function redirectToClientLoginIfUnauthorised(status) {
  if (status === 401) {
    credentialsStore.logout();
    router.push('/clients/login');
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getUserMeNo401Redirect() {
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
      validateStatus: (status) => redirectToClientLoginIfUnauthorised(status),
    });
  },
  getClientByEmail(emailAddress) {
    return axiosClient.get('/clients', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      params: {
        email_address: emailAddress,
      },
    });
  },
  postNewClient(clientData) {
    return axiosClient.post('/client', clientData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getEmailAddressSuggestions(emailAddress) {
    return axiosClient.get('/clients/email-address-suggestions', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      params: {
        email_address: emailAddress,
      },
    });
  },
  getClientIdEmailAddress(emailAddress) {
    return axiosClient.get('/client/id-by-email', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      params: {
        email_address: emailAddress,
      },
    });
  },
  getBikeMakeSuggestions(make) {
    return axiosClient.get('/bikes/suggest/makes', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      params: {
        make: make,
      },
    });
  },
  getBikeModelSuggestions(model) {
    return axiosClient.get('/bikes/suggest/models', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      params: {
        model: model,
      },
    });
  },
  getBikeSerialNumberSuggestions(serialNumber) {
    return axiosClient.get('/bikes/suggest/serial-numbers', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      params: {
        serial_number: serialNumber,
      },
    });
  },
  getBikeColourSuggestions(colour) {
    return axiosClient.get('/bikes/suggest/colours', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      params: {
        colour: colour,
      },
    });
  },
  findBike(make, model, colour, decals, serialNumber) {
    return axiosClient.get('/bike/find', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      params: {
        make: make,
        model: model,
        colour: colour,
        decals: decals,
        serial_number: serialNumber,
      },
    });
  },
  findBikes(make, model, colour, serialNumber) {
    return axiosClient.get('/bikes/find', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      params: {
        ...(make && {make: make.toLowerCase()}),
        ...(model && {model: model.toLowerCase()}),
        ...(colour && {colour: colour.toLowerCase()}),
        ...(serialNumber && {serial_number: serialNumber.toLowerCase()}),
      },
    });
  },
  getBike(bikeId) {
    return axiosClient.get(`/bikes/${bikeId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getContractTypes() {
    return axiosClient.get('/contract/types', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getBikeConditions() {
    return axiosClient.get('/bike/conditions', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getDepositBearers() {
    return axiosClient.get('/users/deposit-bearers', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getActiveUsers() {
    return axiosClient.get('/users/active-users', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getRentalCheckers() {
    return axiosClient.get('/users/rental-checkers', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  findClient(firstName, lastName, emailAddress) {
    return axiosClient.get('/clients/find', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getClientContracts(clientId, open, closed, expired) {
    return axiosClient.get(`/clients/${clientId}/contracts`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToClientLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getUser(userId) {
    return axiosClient.get(`/users/${userId}/`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchExtendContract(contractId) {
    return axiosClient.patch(`/contracts/${contractId}/extend`, null, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
  getAppointmentTypes(inactive=false) {
    return axiosClient.get('/appointments/types', {
      params: {
        inactive: inactive,
      },
    });
  },
  getAvailableAppointmentSlots(appointmentTypeId, ignoreLimits=undefined) {
    return axiosClient.get('/appointments/available', {
      params: {
        appointment_type_id: appointmentTypeId,
        ...ignoreLimits && {ignore_limits: ignoreLimits},
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      params: ignoreLimits && {ignore_limits: ignoreLimits},
    });
  },
  getMyAppointments(past, future) {
    return axiosClient.get('/clients/me/appointments', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToClientLoginIfUnauthorised(status),
    });
  },
  getClientAppointments(clientId, past, future) {
    return axiosClient.get(`/clients/${clientId}/appointments`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getAppointmentType(typeId) {
    return axiosClient.get(`/appointments/types/${typeId}`);
  },
  getMyContract(contractId) {
    return axiosClient.get(`/clients/me/contracts/${contractId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToClientLoginIfUnauthorised(status),
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
    return axiosClient.get('/appointments/calendar', {
      params: {
        start_datetime: startDate,
        end_datetime: endDate,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  confirmAppointment(appointmentId) {
    return axiosClient.patch(`/appointments/${appointmentId}/confirm`, {}, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  cancelAppointment(appointmentId) {
    return axiosClient.patch(`/appointments/${appointmentId}/cancel`, {}, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getDepositBook() {
    return axiosClient.get('/finances/deposit-book', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getUsers() {
    return axiosClient.get('/users', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchUser(userId, patchData) {
    return axiosClient.patch(`/users/${userId}/`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  postNewUser(username, password, pin, admin, depositBearer, rentalChecker, appointmentManager, treasurer) {
    return axiosClient.post('/user', {
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchAppointmentType(appointmentTypeId, patchData) {
    return axiosClient.patch(`/appointments/types/${appointmentTypeId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  postNewAppointmentType(newAppointmentTypeData) {
    return axiosClient.post('/appointments/types', newAppointmentTypeData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchAppointmentGeneralSettings(changedAppointmentGeneralSettings) {
    return axiosClient.patch('/settings/appointments/general', changedAppointmentGeneralSettings, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getAppointmentGeneralSettings() {
    return axiosClient.get('/settings/appointments/general', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  deleteClosedDay(closedDayDate) {
    return axiosClient.delete(`/settings/closed-day/${closedDayDate}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  postClosedDay(closedDay) {
    return axiosClient.post('/settings/closed-day', closedDay, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getAppointmentConcurrencyLimits() {
    return axiosClient.get('/settings/appointments/concurrency', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchAppointmentConcurrencyLimit(afterTime, patchData) {
    return axiosClient.patch(`/settings/appointments/concurrency/${afterTime}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  postNewAppointmentConcurrencyLimit(newConcurrencyLimitData) {
    return axiosClient.post('/settings/appointments/concurrency', newConcurrencyLimitData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  deleteAppointmentConcurrencyLimit(afterTime) {
    return axiosClient.delete(`/settings/appointments/concurrency/${afterTime}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  cancelMyAppointment(appointmentId) {
    return axiosClient.patch(`/clients/me/appointments/${appointmentId}/cancel`, null, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToClientLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getPaperIdSuggestions(paperId) {
    return axiosClient.get('/contracts/paper/suggestions', {
      params: {
        old_id: paperId,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getContractIdFromPaperId(paperId) {
    return axiosClient.get('/contracts/paper', {
      params: {
        paper_id: paperId,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getUserLeaderboard() {
    return axiosClient.get('/statistics/users/leaderboard', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getClientLeaderboard() {
    return axiosClient.get('/statistics/clients/leaderboard', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getBikeLeaderboard() {
    return axiosClient.get('/statistics/bikes/leaderboard', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchBikeChangeDetails(bikeId, patchData) {
    return axiosClient.patch(`/bikes/${bikeId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchContractChangeDetails(contractId, patchData) {
    return axiosClient.patch(`/contracts/${contractId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  postPreBecycleSurvey(surveyAnswers) {
    return axiosClient.post('/surveys/pre-becycle', surveyAnswers, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToClientLoginIfUnauthorised(status),
    });
  },
  postPeriBecycleSurvey(surveyAnswers) {
    return axiosClient.post('/surveys/peri-becycle', surveyAnswers, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToClientLoginIfUnauthorised(status),
    });
  },
  postPostBecycleSurvey(surveyAnswers) {
    return axiosClient.post('/surveys/post-becycle', surveyAnswers, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToClientLoginIfUnauthorised(status),
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
    });
  },
  getRoadSegmentReportTypes() {
    return axiosClient.get('/maps/report-types');
  },
  postNewRoadSegmentReport(roadSegmentId, roadSegmentReportTypeId) {
    return axiosClient.post('/maps/road-segment/report', {
      roadSegmentId: roadSegmentId,
      roadSegmentReportTypeId: roadSegmentReportTypeId,
    });
  },
  refreshPotentialDuplicateClients() {
    return axiosClient.get('/admin/duplicates/clients/refresh', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getPotentialDuplicateClients() {
    return axiosClient.get('/admin/duplicates/clients', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchIgnorePotentialClientDuplicate(clientDuplicateId) {
    return axiosClient.patch(`/admin/duplicates/clients/${clientDuplicateId}/ignore`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  putResolvePotentialClientDuplicate(clientDuplicateId, keepClientId, discardClientId) {
    return axiosClient.put(`/admin/duplicates/clients/${clientDuplicateId}/resolve`, {
      discard_client_id: discardClientId,
      keep_client_id: keepClientId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  refreshPotentialDuplicateBikes() {
    return axiosClient.get('/admin/duplicates/bikes/refresh', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getPotentialDuplicateBikes() {
    return axiosClient.get('/admin/duplicates/bikes', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchIgnorePotentialBikeDuplicate(bikeDuplicateId) {
    return axiosClient.patch(`/admin/duplicates/bikes/${bikeDuplicateId}/ignore`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  putResolvePotentialBikeDuplicate(bikeDuplicateId, keepBikeId, discardBikeId) {
    return axiosClient.put(`/admin/duplicates/bikes/${bikeDuplicateId}/resolve`, {
      discard_bike_id: discardBikeId,
      keep_bike_id: keepBikeId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  downloadRawDataExcel() {
    return axiosClient.get('/admin/takeout/contracts.xlsx', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      responseType: 'blob',
    });
  },
  downloadRawDataPdf() {
    return axiosClient.get('/admin/takeout/contracts.pdf', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      responseType: 'blob',
    });
  },
  getContracts() {
    return axiosClient.get('/contracts', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  deleteContract(contractId) {
    return axiosClient.delete(`/contracts/${contractId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getNextClosedDay() {
    return axiosClient.get('/public/next-closed-day');
  },
  getAddress() {
    return axiosClient.get('/public/address');
  },
  putAddress(newAddress) {
    return axiosClient.put('/settings/address', newAddress, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getDepositExchangeUsers() {
    return axiosClient.get('/deposit-exchanges/users', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getPercentageDepositReturnedAfterMonths(startDate, endDate) {
    return axiosClient.get('/finances/deposits/return-percentage', {
      params: {
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getWorstCaseRequiredDepositFloat() {
    return axiosClient.get('/finances/deposits/required-float/worst-case', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getRealisticRequiredDepositFloat(gracePeriod) {
    return axiosClient.get('/finances/deposits/required-float/realistic', {
      params: {
        grace_period: gracePeriod,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getExpenseTypes() {
    return axiosClient.get('/expenses/types', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getExpenseTags(inactive=false) {
    return axiosClient.get('/expenses/tags', {
      params: {
        inactive: inactive,
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getExpenses(filterByTag=null) {
    return axiosClient.get('/expenses', {
      params: filterByTag ? {tag: filterByTag} : null,
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchExpenseTransferred(expenseId) {
    return axiosClient.patch(`/expenses/${expenseId}/transfer`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  deleteExpense(expenseId) {
    return axiosClient.delete(`/expenses/${expenseId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getExpenseReceipt(expenseId) {
    return axiosClient.get(`/expenses/${expenseId}/receipt`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
      responseType: 'blob',
    });
  },
  getActualCashflow(interval, startDate, endDate, tag) {
    return axiosClient.get('/finances/cashflow/actual', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
        ...(tag && {tag: tag}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getProvisionalCashflow(interval, startDate, endDate, tag) {
    return axiosClient.get('/finances/cashflow/provisional', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
        ...(tag && {tag: tag}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getTotalCashflow(interval, startDate, endDate, tag) {
    return axiosClient.get('/finances/cashflow/total', {
      params: {
        interval: interval,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
        ...(tag && {tag: tag}),
      },
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getMyPresentationCard() {
    return axiosClient.get('/users/me/presentation-card', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  deleteMyPresentationCard() {
    return axiosClient.delete('/users/me/presentation-card', {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  getPublicUserPresentationCards() {
    return axiosClient.get('/public/users/presentation-cards');
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
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  deleteUserPresentationCardDetails(presentationCardId) {
    return axiosClient.delete(`/users/presentation-card/${presentationCardId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  deleteContractType(contractTypeId) {
    return axiosClient.delete(`/settings/contract-types/${contractTypeId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  postContractType(contractTypeId) {
    return axiosClient.post('/settings/contract-types', {
      id: contractTypeId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  deleteExpenseType(expenseTypeId) {
    return axiosClient.delete(`/settings/expense-types/${expenseTypeId}`, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  postNewExpenseType(expenseTypeId, expenseTypeDescription) {
    return axiosClient.post('/settings/expense-types', {
      id: expenseTypeId,
      description: expenseTypeDescription,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchExpenseType(expenseTypeId, expenseTypeDescription) {
    return axiosClient.patch(`/settings/expense-types/${expenseTypeId}`, {
      description: expenseTypeDescription,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  postNewExpenseTag(expenseTagId, expenseTagDescription) {
    return axiosClient.post('/expenses/tags', {
      id: expenseTagId,
      description: expenseTagDescription,
      active: true,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
  patchExpenseTag(expenseTagId, expenseTagDescription, expenseTagActive) {
    return axiosClient.patch(`/expenses/tags/${expenseTagId}`, {
      description: expenseTagDescription,
      active: expenseTagActive,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
      validateStatus: (status) => redirectToUserLoginIfUnauthorised(status),
    });
  },
};
