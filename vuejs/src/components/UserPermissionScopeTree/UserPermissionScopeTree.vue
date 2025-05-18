<script lang="ts">
import Checkbox from '@/components/Checkbox/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import {Icon} from '@iconify/vue';

const toast = useToast();

export default {
  name: 'UserPermissionScopeTree',
  components: {Icon, Checkbox},
  emits: [
    'userPermissionAdded',
    'userPermissionRemoved',
  ],
  props: {
    tree: {
      type: Object,
      default: () => {
        return {};
      },
    },
    userId: {
      type: String,
      required: true,
    },
    userPermissions: {
      type: Array,
      required: true,
    },
    userPermissionsAtPredecessor: {
      type: Object,
      default: () => {
        return {
          GET: false,
          POST: false,
          PUT: false,
          PATCH: false,
          DELETE: false,
        };
      },
    },
  },
  methods: {
    toggleUserPermission(event, method) {
      console.log('current state', this.userHasPermissionModelValues);
      const granted = this.userHasPermissionModelValues[method];
      console.log('setting', granted, method, this.tree.route);

      if (granted) {
        requests.addUserPermission(this.userId, this.tree.permissionIds[method])
          .then((response) => {
            toast.success('Permission granted', {timeout: 2000});
            this.$emit('userPermissionAdded', response.data.permissionScopeId);
          })
          .catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 2000});
          });
      } else {
        requests.removeUserPermission(this.userId, this.tree.permissionIds[method])
          .then((response) => {
            toast.success('Permission revoked', {timeout: 2000});
            this.$emit('userPermissionRemoved', response.data);
          }).catch((error) => {
            toast.error(error.response.data.detail.description, {timeout: 2000});
          });
      }
    },
    anyChildrenHavePermission(tree, method) {
      for (const child of tree.childNodes) {
        if (this.userPermissions.includes(child.permissionIds[method])) {
          return true;
        }
        if (this.anyChildrenHavePermission(child, method)) {
          return true;
        }
      }
      return false;
    },
    getModelValueForMethod(method) {
      let result = false;
      if (!Object.hasOwn(this.tree.permissionIds, method)) {
        result = false;
      }
      if (this.userPermissions.includes(this.tree.permissionIds[method]) ||
          this.userPermissionsAtPredecessor[method] === true) {
        result = true;
      }
      if (this.anyChildrenHavePermission(this.tree, method)) {
        result = null;
      }
      return result;
    },
  },
  data() {
    return {
      methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
      expandChildren: false,
    };
  },
  computed: {
    userHasPermissionModelValues: {
      get() {
        return {
          GET: this.getModelValueForMethod('GET'),
          POST: this.getModelValueForMethod('POST'),
          PUT: this.getModelValueForMethod('PUT'),
          PATCH: this.getModelValueForMethod('PATCH'),
          DELETE: this.getModelValueForMethod('DELETE'),
        };
      },
    },
  },
};
</script>

<template>
      <div class="col-span-1">
        <Icon
            v-if="tree.childNodes.length > 0"
            :icon="expandChildren ? 'heroicons-outline:chevron-down' : 'heroicons-outline:chevron-right'"
            @click="expandChildren = !expandChildren"/>
      </div>
      <div class="col-span-8">{{tree.route}}</div>
      <div class="col-span-3 grid grid-cols-5">
        <div class="col-span-1 justify-items-center">
          <Checkbox
              v-if="Object.hasOwn(tree.permissionIds, 'GET')"
              :name="tree.route + 'GET'"
              activeClass="ring-primary-500 bg-primary-500"
              v-model="userHasPermissionModelValues.GET"
              allow-null
              :disabled="userPermissionsAtPredecessor['GET'] === true"
              @change="(event) => toggleUserPermission(event, 'GET')"
          />
        </div>
        <div class="col-span-1 justify-items-center">
          <Checkbox
              v-if="Object.hasOwn(tree.permissionIds, 'POST')"
              :name="tree.route + 'POST'"
              activeClass="ring-primary-500 bg-primary-500"
              v-model="userHasPermissionModelValues.POST"
              allow-null
              :disabled="userPermissionsAtPredecessor['POST'] === true"
              @change="(event) => toggleUserPermission(event, 'POST')"
          />
        </div>
        <div class="col-span-1 justify-items-center">
          <Checkbox
              v-if="Object.hasOwn(tree.permissionIds, 'PUT')"
              :name="tree.route + 'PUT'"
              activeClass="ring-primary-500 bg-primary-500"
              v-model="userHasPermissionModelValues.PUT"
              allow-null
              :disabled="userPermissionsAtPredecessor['PUT'] === true"
              @change="(event) => toggleUserPermission(event, 'PUT')"
          />
        </div>
        <div class="col-span-1 justify-items-center">
          <Checkbox
              v-if="Object.hasOwn(tree.permissionIds, 'PATCH')"
              :name="tree.route + 'PATCH'"
              activeClass="ring-primary-500 bg-primary-500"
              v-model="userHasPermissionModelValues.PATCH"
              allow-null
              :disabled="userPermissionsAtPredecessor['PATCH'] === true"
              @change="(event) => toggleUserPermission(event, 'PATCH')"
          />
        </div>
        <div class="col-span-1 justify-items-center">
          <Checkbox
              v-if="Object.hasOwn(tree.permissionIds, 'DELETE')"
              :name="tree.route + 'DELETE'"
              activeClass="ring-primary-500 bg-primary-500"
              v-model="userHasPermissionModelValues.DELETE"
              allow-null
              :disabled="userPermissionsAtPredecessor['DELETE'] === true"
              @change="(event) => toggleUserPermission(event, 'DELETE')"
          />
        </div>
      </div>
      <template v-if="expandChildren">
        <div class="col-span-1"></div>
        <div class="col-span-11">
          <div class="grid grid-cols-12 border-solid border-slate-300 border">
            <div class="col-span-1"></div>
            <div class="col-span-8">Route</div>
            <div class="col-span-3 grid grid-cols-5">
              <div class="col-span-1 text-center" v-for="method in methods" :key="method">{{method}}</div>
            </div>
            <template  v-for="subTree in tree.childNodes" :key="subTree.route">
                <UserPermissionScopeTree
                    :tree="subTree"
                    :user-id="userId"
                    :user-permissions-at-predecessor="userHasPermissionModelValues"
                    :user-permissions="userPermissions"
                    @user-permission-added="(permissionScopeId) => $emit('userPermissionAdded', permissionScopeId)"
                    @user-permission-removed="(permissionScopeId) => $emit('userPermissionRemoved', permissionScopeId)"
                ></UserPermissionScopeTree>
            </template>
          </div>
        </div>
      </template>
</template>

<style scoped lang="scss">

</style>
