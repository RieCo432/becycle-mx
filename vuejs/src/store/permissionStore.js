import {defineStore} from 'pinia';
import {useCredentialsStore} from '@/store/credentialsStore';
import ENDPOINTS from '@/constant/endpoints';

// This store is reachable from main.js / App.vue's early import graph, which is
// evaluated before `app.use(pinia)`. `requests/index.js` calls a `use*Store()`
// helper at module scope, so it cannot be imported here at module load. The
// endpoint registry (`@/constant/endpoints`) is side-effect-free and safe to
// import eagerly. So `load()` defers the `requests` import to runtime, and
// `can()` reads the (side-effect-free) registry synchronously.

// Normalize a (method, route) pair into a single lookup key shared by both the
// grants from GET /users/me/permissions and the keys we check against. This
// unifies path-parameter naming (backend `{user_id}` vs JS `{userId}`),
// method case, and any query string the caller may attach.
function normalizeKey(method, route) {
  const methodPart = String(method ?? '').trim().toUpperCase();
  let routePart = String(route ?? '').trim();

  const qIndex = routePart.indexOf('?');
  if (qIndex !== -1) routePart = routePart.slice(0, qIndex);

  routePart = routePart
    .split('/')
    .map((segment) => (segment.startsWith('{') && segment.endsWith('}') ? '*' : segment))
    .join('/')
    .toLowerCase();

  return `${methodPart}:${routePart}`;
}

export const usePermissionStore = defineStore('permissionStore', {
  state: () => ({
    // Set of normalized "METHOD:/route/with/*/params" keys a logged-in user is
    // allowed to call, populated by `load`. The backend is the enforcement
    // boundary; this only drives which buttons/features the UI shows.
    permissions: new Set(),
    loaded: false,
    loading: false,
  }),
  actions: {
    async load() {
      const credentialsStore = useCredentialsStore();
      if (this.loading || this.loaded) return;
      if (!credentialsStore.isUserLoggedIn()) return;
      this.loading = true;
      try {
        const {default: requests} = await import('@/requests');
        const response = await requests.getUserPermissionsMe();
        const keys = new Set();
        for (const permission of (response.data ?? [])) {
          if (permission && permission.method && permission.route) {
            keys.add(normalizeKey(permission.method, permission.route));
          }
        }
        this.permissions = keys;
        this.loaded = true;
      } catch (error) {
        // Fail closed: keep the set empty and allow a retry on a later call.
        console.error('Failed to load permissions', error);
        this.reset();
      } finally {
        this.loading = false;
      }
    },
    // Accepts either an action name from the endpoint registry —
    //   can('patchUser')                                  -> PATCH /users/{id}
    // — or an explicit (method, route) pair one-off —
    //   can('PATCH', '/users/{id}')
    can(actionOrMethod, maybeRoute) {
      const credentialsStore = useCredentialsStore();
      if (!credentialsStore.isUserLoggedIn()) return false;
      if (this.permissions.size === 0) return false;

      let method;
      let route;
      if (typeof actionOrMethod === 'string' && maybeRoute === undefined && ENDPOINTS[actionOrMethod]) {
        ({method, route} = ENDPOINTS[actionOrMethod]);
      } else {
        method = actionOrMethod;
        route = maybeRoute;
      }

      return this.permissions.has(normalizeKey(method, route));
    },
    reset() {
      this.permissions = new Set();
      this.loaded = false;
      this.loading = false;
    },
  },
});
