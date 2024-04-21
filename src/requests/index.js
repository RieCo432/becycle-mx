import axios from 'axios';
import {useCredentialsStore} from '@/store/credentialsStore';


const credentialsStore = useCredentialsStore();
const API_PROTOCOL = import.meta.env.VITE_API_PROTOCOL;
const API_HOST = import.meta.env.VITE_API_HOST;
const API_PORT = import.meta.env.VITE_API_PORT;
const API_SUBDIR = import.meta.env.VITE_API_SUBDIR;

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
  findBikes(make, model, colour, serialNumber) {
    return axiosClient.get('/bikes/find', {
      headers: credentialsStore.getApiRequestHeader(),
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
  getBikeContracts(bikeId, open, closed, expired) {
    return axiosClient.get(`/bikes/${bikeId}/contracts`, {
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
  getAppointmentTypes(inactive=false) {
    return axiosClient.get('/appointments/types', {
      params: {
        inactive: inactive,
      },
    });
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
    return axiosClient.get('/appointments/calendar', {
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
  getDepositBook() {
    return axiosClient.get('/finances/deposit-book', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getUsers() {
    return axiosClient.get('/users', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchUser(userId, patchData) {
    return axiosClient.patch(`/users/${userId}/`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
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
    });
  },
  patchAppointmentType(appointmentTypeId, patchData) {
    return axiosClient.patch(`/appointments/types/${appointmentTypeId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  postNewAppointmentType(newAppointmentTypeData) {
    return axiosClient.post('/appointments/types', newAppointmentTypeData, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchAppointmentGeneralSettings(changedAppointmentGeneralSettings) {
    return axiosClient.patch('/settings/appointments/general', changedAppointmentGeneralSettings, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getAppointmentGeneralSettings() {
    return axiosClient.get('/settings/appointments/general', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  deleteClosedDay(closedDayDate) {
    return axiosClient.delete(`/settings/closed-day/${closedDayDate}`, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  postClosedDay(closedDay) {
    return axiosClient.post('/settings/closed-day', closedDay, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getAppointmentConcurrencyLimits() {
    return axiosClient.get('/settings/appointments/concurrency', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchAppointmentConcurrencyLimit(afterTime, patchData) {
    return axiosClient.patch(`/settings/appointments/concurrency/${afterTime}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  postNewAppointmentConcurrencyLimit(newConcurrencyLimitData) {
    return axiosClient.post('/settings/appointments/concurrency', newConcurrencyLimitData, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  deleteAppointmentConcurrencyLimit(afterTime) {
    return axiosClient.delete(`/settings/appointments/concurrency/${afterTime}`, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  cancelMyAppointment(appointmentId) {
    return axiosClient.patch(`/clients/me/appointments/${appointmentId}/cancel`, null, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  postDepositExchange(amount, fromUsername, fromPassword, toUsername, toPassword) {
    const headers = credentialsStore.getApiRequestHeader();
    console.log(headers);
    return axiosClient.post('/deposit-exchanges', {
      amount: amount,
      deposit_returning_username: fromUsername,
      deposit_returning_user_password: fromPassword,
      deposit_receiving_username: toUsername,
      deposit_receiving_user_password: toPassword,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getPaperIdSuggestions(paperId) {
    return axiosClient.get('/contracts/paper/suggestions', {
      params: {
        old_id: paperId,
      },
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getContractIdFromPaperId(paperId) {
    return axiosClient.get('/contracts/paper', {
      params: {
        paper_id: paperId,
      },
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getUserLeaderboard() {
    return axiosClient.get('/statistics/users/leaderboard', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getClientLeaderboard() {
    return axiosClient.get('/statistics/clients/leaderboard', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getBikeLeaderboard() {
    return axiosClient.get('/statistics/bikes/leaderboard', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchChangeNames(patchData) {
    return axiosClient.patch('/clients/me', patchData, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchClientChangeDetails(clientId, patchData) {
    return axiosClient.patch(`/clients/${clientId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchBikeChangeDetails(bikeId, patchData) {
    return axiosClient.patch(`/bikes/${bikeId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchContractChangeDetails(contractId, patchData) {
    return axiosClient.patch(`/contracts/${contractId}`, patchData, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getTotalContractsDateSeries(interval, breakdown, startDate=null, endDate=null) {
    return axiosClient.get('/statistics/contracts/total', {
      params: {
        interval: interval,
        breakdown: breakdown,
        ...(startDate && {start: startDate}),
        ...(endDate && {end: endDate}),
      },
      headers: credentialsStore.getApiRequestHeader(),
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
    });
  },
  postPreBecycleSurvey(surveyAnswers) {
    return axiosClient.post('/surveys/pre-becycle', surveyAnswers, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  postPeriBecycleSurvey(surveyAnswers) {
    return axiosClient.post('/surveys/peri-becycle', surveyAnswers, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  postPostBecycleSurvey(surveyAnswers) {
    return axiosClient.post('/surveys/post-becycle', surveyAnswers, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getGeoJson() {
    return axiosClient.get('/maps/geojson');
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
    });
  },
  getPotentialDuplicateClients() {
    return axiosClient.get('/admin/duplicates/clients', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchIgnorePotentialClientDuplicate(clientDuplicateId) {
    return axiosClient.patch(`/admin/duplicates/clients/${clientDuplicateId}/ignore`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  putResolvePotentialClientDuplicate(clientDuplicateId, keepClientId, discardClientId) {
    return axiosClient.put(`/admin/duplicates/clients/${clientDuplicateId}/resolve`, {
      discard_client_id: discardClientId,
      keep_client_id: keepClientId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  refreshPotentialDuplicateBikes() {
    return axiosClient.get('/admin/duplicates/bikes/refresh', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  getPotentialDuplicateBikes() {
    return axiosClient.get('/admin/duplicates/bikes', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  patchIgnorePotentialBikeDuplicate(bikeDuplicateId) {
    return axiosClient.patch(`/admin/duplicates/bikes/${bikeDuplicateId}/ignore`, undefined, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  putResolvePotentialBikeDuplicate(bikeDuplicateId, keepBikeId, discardBikeId) {
    return axiosClient.put(`/admin/duplicates/bikes/${bikeDuplicateId}/resolve`, {
      discard_bike_id: discardBikeId,
      keep_bike_id: keepBikeId,
    }, {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  downloadRawDataExcel() {
    return axiosClient.get('/admin/takeout/contracts.xlsx', {
      headers: credentialsStore.getApiRequestHeader(),
      responseType: 'blob',
    });
  },
  downloadRawDataPdf() {
    return axiosClient.get('/admin/takeout/contracts.pdf', {
      headers: credentialsStore.getApiRequestHeader(),
      responseType: 'blob',
    });
  },
  getContracts() {
    return axiosClient.get('/contracts', {
      headers: credentialsStore.getApiRequestHeader(),
    });
  },
  deleteContract(contractId) {
    return axiosClient.delete(`/contracts/${contractId}`, {
      headers: credentialsStore.getApiRequestHeader(),
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
    });
  },
};
