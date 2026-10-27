// Permission endpoint registry — the single, importable source of truth for
// "what endpoint does UI action X require?".
//
// Kept side-effect-free (no imports) so it can be imported from ANYwhere —
// including the pinia permission store and components that live in main.js's
// early import graph — without pulling in `requests/index.js`, which calls
// useCredentialsStore() at module scope and would otherwise run before pinia
// is installed.
//
// Keys intentionally mirror the `requests/*` action names, so the handle a
// button already references (the request it fires) is also the handle it gates
// on. Route strings use the backend parameter names; `normalizeKey` wildcard-
// matches them against the grants returned by GET /users/me/permissions, so
// `{user_id}` here and `{userId}` in the axios transport URL both resolve to
// `*` and match.
//
// The server remains the enforcement boundary; anything a user over-permits by
// clicking a visible button is still 403'd there. This registry only drives
// which buttons the UI shows, so a name here maps to *one* HTTP endpoint.
export const ENDPOINTS = {
  // users & roles -----------------------------------------------------------
  patchUser: {method: 'PATCH', route: '/users/{user_id}'},
  postNewUser: {method: 'POST', route: '/users'},
  addUserPermission: {method: 'POST', route: '/users/{user_id}/permissions'},
  removeUserPermission: {method: 'DELETE', route: '/users/{user_id}/permissions/{permission_id}'},
  postUserGroup: {method: 'POST', route: '/groups'},
  deleteUserGroup: {method: 'DELETE', route: '/groups/{group_id}'},
  addGroupPermission: {method: 'POST', route: '/groups/{group_id}/permissions'},
  removeGroupPermission: {method: 'DELETE', route: '/groups/{group_id}/permissions/{permission_id}'},
  addGroupUser: {method: 'POST', route: '/groups/{group_id}/users'},
  removeGroupUser: {method: 'DELETE', route: '/groups/{group_id}/users/{user_id}'},

  // contracts ---------------------------------------------------------------
  patchContractChangeDetails: {method: 'PATCH', route: '/contracts/{contract_id}'},
  deleteContract: {method: 'DELETE', route: '/contracts/{contract_id}'},
  patchContractForfeit: {method: 'PATCH', route: '/contracts/{contract_id}/forfeit'},

  // expenses & claims -------------------------------------------------------
  postNewExpenseClaim: {method: 'POST', route: '/expenses/claims'},
  putExpenseClaim: {method: 'PUT', route: '/expenses/claims/{expense_claim_id}'},
  deleteExpenseClaim: {method: 'DELETE', route: '/expenses/claims/{expense_claim_id}'},
  patchExpenseClaimReimbursed: {method: 'PATCH', route: '/expenses/claims/{expense_claim_id}/reimburse'},

  // settings ----------------------------------------------------------------
  putAddress: {method: 'PUT', route: '/settings/address'},
  patchAboutUs: {method: 'PATCH', route: '/settings/about-us'},
  patchFaq: {method: 'PATCH', route: '/settings/faq/{faq_id}'},
  postFaq: {method: 'POST', route: '/settings/faq'},
  swapFaq: {method: 'PATCH', route: '/settings/faq/swap'},
  postContractType: {method: 'POST', route: '/settings/contract-types'},
  deleteContractType: {method: 'DELETE', route: '/settings/contract-types/{contract_type_id}'},
  patchAppointmentConcurrencyLimit: {method: 'PATCH', route: '/settings/appointments/concurrency/{weekday}/{after_time}'},
  deleteAppointmentConcurrencyLimit: {method: 'DELETE', route: '/settings/appointments/concurrency/{weekday}/{after_time}'},
  postAppointmentConcurrencyLimit: {method: 'POST', route: '/settings/appointments/concurrency'},
  patchAppointmentGeneralSettings: {method: 'PATCH', route: '/settings/appointments/general'},
  postNewCatalogueItem: {method: 'POST', route: '/catalogue'},
  putUpdateCatalogueItem: {method: 'PUT', route: '/catalogue/{catalogue_item_id}'},
  patchCatalogueItemAvailability: {method: 'PATCH', route: '/catalogue/{catalogue_item_id}/availability'},


  // appointments ------------------------------------------------------------
  confirmAppointment: {method: 'PATCH', route: '/appointments/{appointment_id}/confirm'},
  cancelAppointment: {method: 'PATCH', route: '/appointments/{appointment_id}/cancel'},
  patchAppointmentReschedule: {method: 'PATCH', route: '/appointments/{appointment_id}/reschedule'},
  patchAppointmentDidClientShowUp: {method: 'PATCH', route: '/appointments/{appointment_id}/showup'},
  AppointmentDidClientShowUp: {method: 'PATCH', route: '/appointments/{appointment_id}/showup'},
  postNewAppointmentType: {method: 'POST', route: '/appointments/types'},
  patchAppointmentType: {method: 'PATCH', route: '/appointments/types/{appointment_type_id}'},
  swapAppointmentTypes: {method: 'PATCH', route: '/settings/appointments/swap'},

  // photos ------------------------------------------------------------------
  getPhotos: {method: 'GET', route: '/photos'},
  postNewPhotos: {method: 'POST', route: '/photos'},
  deletePhoto: {method: 'DELETE', route: '/photos/{photo_id}'},

  // presentation cards ------------------------------------------------------
  postUserPresentationCardDetails: {method: 'POST', route: '/users/presentation-card/{presentation_card_id}'},
  deleteUserPresentationCardDetails: {method: 'DELETE', route: '/users/presentation-card/{presentation_card_id}'},

  // dashboards --------------------------------------------------------------
  putDashboardUpdate: {method: 'PUT', route: '/dashboards/{dashboard_id}'},
  postNewDashboard: {method: 'POST', route: '/dashboards'},
  deleteDashboard: {method: 'DELETE', route: '/dashboards/{dashboard_id}'},
  patchMoveDashboardUp: {method: 'PATCH', route: '/dashboards/{dashboard_id}/up'},
  patchMoveDashboardDown: {method: 'PATCH', route: '/dashboards/{dashboard_id}/down'},

  // transactions ------------------------------------------------------------
  createTransaction: {method: 'POST', route: '/transactions'},

  // accounts ----------------------------------------------------------------
  postNewAccount: {method: 'POST', route: '/accounts'},
  closeAccount: {method: 'PATCH', route: '/accounts/{account_id}/close'},
  reopenAccount: {method: 'PATCH', route: '/accounts/{account_id}/reopen'},
  putUpdateAccount: {method: 'PUT', route: '/accounts/{account_id}'},

  // duplicates --------------------------------------------------------------
  putResolvePotentialBikeDuplicate: {method: 'PUT', route: '/admin/duplicates/bikes/{potential_bike_duplicate_id}/resolve'},
  patchIgnorePotentialBikeDuplicate: {method: 'PATCH', route: '/admin/duplicates/bikes/{potential_bike_duplicate_id}/ignore'},
  putResolvePotentialClientDuplicate: {method: 'PUT', route: '/admin/duplicates/clients/{potential_client_duplicate_id}/resolve'},
  patchIgnorePotentialClientDuplicate: {method: 'PATCH', route: '/admin/duplicates/clients/{potential_client_duplicate_id}/ignore'},
  
  // takeout -----------------------------------------------------------------
  downloadRawDataPdf: {method: 'GET', route: '/admin/takeout/contracts.pdf'},
  downloadRawDataExcel: {method: 'GET', route: '/admin/takeout/contracts.xlsx'},
  
  // bug reports -------------------------------------------------------------
  deleteBugReport: {method: 'DELETE', route: '/bugreports/{bug_report_id}'},
  mergeBugReports: {method: 'POST', route: '/bugreports/merge'},
  patchBugReport: {method: 'PATCH', route: '/bugreports/{bug_report_id}'},
  createBugReport: {method: 'POST', route: '/bugreports'},
};

export default ENDPOINTS;
