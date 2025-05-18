<script lang="ts">
import {defineComponent} from 'vue';
import Checkbox from '@/components/Checkbox/index.vue';
import requests from '@/requests';
import {useToast} from 'vue-toastification';
import DashButton from '@/components/Button/index.vue';
import {exp} from '@amcharts/amcharts5/.internal/core/util/Ease';

const toast = useToast();

export default defineComponent({
  name: 'UserPermissionScopeTree',
  components: {DashButton, Checkbox},
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
    userPermissions: {
      type: Array,
      default: () => [],
    },
    userId: {
      type: String,
      required: true,
    },
    userPermissionsAtPredecessor: {
      type: Object,
      default: () => ({
        'GET': false,
        'POST': false,
        'PUT': false,
        'PATCH': false,
        'DELETE': false,
      }),
    },
  },
  methods: {
    exp,
    toggleUserPermission(event, method) {
      console.log(event, method);
      const granted = this.userHasPermissionModelValues[method] !== null && !this.userHasPermissionModelValues[method];
      console.log(granted);
      console.log(this.tree);
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
            this.$emit('userPermissionRemoved', this.tree.permissionIds[method]);
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
        console.log('permissions', this.userPermissions);
        console.log(this.userPermissions.includes(this.tree.permissionIds['GET']));
        const result = {
          'GET': this.userPermissions.includes(this.tree.permissionIds['GET']) || this.userPermissionsAtPredecessor['GET'] === true,
          'POST': this.userPermissions.includes(this.tree.permissionIds['POST']) || this.userPermissionsAtPredecessor['POST'] === true,
          'PUT': this.userPermissions.includes(this.tree.permissionIds['PUT']) || this.userPermissionsAtPredecessor['PUT'] === true,
          'PATCH': this.userPermissions.includes(this.tree.permissionIds['PATCH']) || this.userPermissionsAtPredecessor['PATCH'] === true,
          'DELETE': this.userPermissions.includes(this.tree.permissionIds['DELETE']) || this.userPermissionsAtPredecessor['DELETE'] === true,
        };
        this.methods.forEach((method) => {
          if (!result[method] && this.anyChildrenHavePermission(this.tree, method)) {
            result[method] = null;
          }
        });
        console.log('result', result);
        return result;
      },
    },
  },
});
</script>

<template>
  <div>
    <div class="grid grid-cols-12 gap-2">
      <div class="col-span-1"></div>
      <div class="col-span-6">Route</div>
      <div class="col-span-1" v-for="method in methods" :key="method">{{method}}</div>
      <div class="col-span-1">
        <DashButton
            v-if="tree.childNodes.length > 0"
            class="btn-sm"
            :icon="expandChildren ? 'heroicons-outline:arrow-down' : 'heroicons-outline:arrow-right'"
            @click="expandChildren = !expandChildren"/>
      </div>
      <div class="col-span-6">{{tree.route}}</div>
      <div class="col-span-1" v-for="method in methods" :key="method">
        <Checkbox
            v-if="Object.hasOwn(tree.permissionIds, method)"
            :disabled="userPermissionsAtPredecessor[method]"
            :name="tree.route + method"
            activeClass="ring-primary-500 bg-primary-500"
            :checked="userHasPermissionModelValues[method]"
            allow-null
            @change="(event) => toggleUserPermission(event, method)"
        />
      </div>
      <template v-if="expandChildren">
        <template  v-for="subTree in tree.childNodes" :key="subTree.route">
          <div class="col-span-1"></div>
          <div class="col-span-11">
            <UserPermissionScopeTree
                :tree="subTree"
                :user-permissions="userPermissions"
                :user-id="userId"
                @user-permission-added="(permissionScopeId) => $emit('userPermissionAdded', permissionScopeId)"
                @user-permission-removed="(permissionScopeId) => $emit('userPermissionRemoved', permissionScopeId)"
                :user-permissions-at-predecessor="userHasPermissionModelValues"
            ></UserPermissionScopeTree>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
