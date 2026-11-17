<script>
import Card from '@/components/Card/index.vue';
import TextInput from '@/components/TextInput/index.vue';
import Textarea from '@/components/Textarea/index.vue';
import Button from '@/components/Button/index.vue';
import Switch from '@/components/Switch';
import {useToast} from 'vue-toastification';
import requests from '@/requests';
import {onBeforeMount, ref} from 'vue';
const toast = useToast();

export default {
  name: 'UpdateChatIntentsCard',
  components: {Card, TextInput, Textarea, Button, Switch},
  setup() {
    const intents = ref([]);
    const fragments = ref([]);

    // `name` is the slug + the dispatch key; title-case it for display
    // ("open_today" -> "Open Today").
    const displayName = (name) =>
      String(name ?? '').split(/[_-]+/).filter(Boolean)
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

    const emptyDraft = () => ({name: '', whenToUse: '', replyTemplate: '', enabled: true});

    // Inline edit of an existing intent — its row swaps to inputs while editing.
    const editingId = ref(null);
    const editDraft = ref(emptyDraft());
    // The "add new" row at the bottom.
    const newDraft = ref(emptyDraft());

    const fetchIntents = () => {
      requests.getChatIntents().then((response) => {
        intents.value = response.data ?? [];
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    };
    const fetchFragments = () => {
      requests.getChatIntentFragments().then((response) => {
        fragments.value = response.data ?? [];
      }).catch(() => {});
    };

    const startEdit = (intent) => {
      editingId.value = intent.id;
      editDraft.value = {
        name: intent.name,
        whenToUse: intent.whenToUse ?? '',
        replyTemplate: intent.replyTemplate,
        enabled: intent.enabled,
      };
    };
    const cancelEdit = () => {
      editingId.value = null;
      editDraft.value = emptyDraft();
    };

    const saveEdit = () => {
      if (!editingId.value) return;
      const name = editDraft.value.name.trim();
      if (!name) {
        toast.error('An intent needs a name (its classifier key).', {timeout: 2000});
        return;
      }
      const payload = {
        name,
        whenToUse: editDraft.value.whenToUse.trim() || null,
        replyTemplate: editDraft.value.replyTemplate,
        enabled: editDraft.value.enabled,
      };
      requests.patchChatIntent(editingId.value, payload).then(() => {
        toast.success('Intent updated', {timeout: 2000});
        cancelEdit();
        fetchIntents();
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    };

    const addNew = () => {
      const name = newDraft.value.name.trim();
      if (!name) {
        toast.error('An intent needs a name (its classifier key).', {timeout: 2000});
        return;
      }
      const payload = {
        name,
        whenToUse: newDraft.value.whenToUse.trim() || null,
        replyTemplate: newDraft.value.replyTemplate,
        enabled: newDraft.value.enabled,
        orderIndex: 0,
      };
      requests.postChatIntent(payload).then(() => {
        toast.success('Intent added', {timeout: 2000});
        newDraft.value = emptyDraft();
        fetchIntents();
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    };

    const removeIntent = (intent) => {
      if (!window.confirm(`Delete the "${displayName(intent.name)}" intent?`)) return;
      requests.deleteChatIntent(intent.id).then(() => {
        toast.success('Intent deleted', {timeout: 2000});
        if (editingId.value === intent.id) cancelEdit();
        fetchIntents();
      }).catch((error) => {
        toast.error(error.response.data.detail.description, {timeout: 2000});
      });
    };

    // Append a {{fragment}} token to the given draft's reply (with a separating space).
    // `draft` is the (unwrapped) draft object from the template.
    const insertFragment = (fragmentName, draft) => {
      const token = `{{${fragmentName}}}`;
      const current = draft.replyTemplate ?? '';
      draft.replyTemplate = current && !current.endsWith(' ') ? `${current} ${token}` : `${current}${token}`;
    };

    // Render the double-brace token for a fragment ("open_today" -> "{{open_today}").
    // A helper (not an inline `{{ '{open_today}' }}`) because the template parser would
    // close the interpolation at the first `}}` inside the literal, so we can't write
    // a `{{...}}` token directly in a Vue interpolation.
    const slotToken = (name) => `{{${name}}}`;

    // Client-side dry-run of the backend's template evaluator (crud/intents.py
    // evaluate_template): fill {{fragments}} from each fragment's live `example` so
    // the admin sees the reply a client would actually get. ok=false means a
    // referenced fragment has no data, in which case the real reply would fall
    // through to the free-form fallback instead of being sent pre-formed (the
    // server makes the same call in evaluate_template).
    const previewReply = (template) => {
      const text = (template ?? '').trim();
      if (!text) return {ok: true, display: 'Type a reply to see a live preview'};
      const SLOT = /\{\{\s*([a-z0-9_]+)\s*\}\}/g;
      const fragMap = Object.fromEntries((fragments.value ?? []).map((f) => [f.name, f]));
      const names = [...text.matchAll(SLOT)].map((m) => m[1]);
      if (names.length === 0) return {ok: true, display: text};
      const missing = [...new Set(names)].filter((name) => {
        const frag = fragMap[name];
        return !frag || frag.example == null || String(frag.example).trim() === '';
      });
      const display = text.replace(SLOT, (m, name) => {
        const frag = fragMap[name];
        const val = frag && frag.example != null ? String(frag.example).trim() : '';
        return val || m;
      });
      if (missing.length) {
        return {ok: false, display: `${display}   (would fall through — no data for: ${missing.join(', ')})`};
      }
      return {ok: true, display};
    };

    onBeforeMount(() => {
      fetchIntents();
      fetchFragments();
    });

    return {
      intents,
      fragments,
      displayName,
      editingId,
      editDraft,
      newDraft,
      startEdit,
      cancelEdit,
      saveEdit,
      addNew,
      removeIntent,
      insertFragment,
      slotToken,
      previewReply,
    };
  },
};
</script>

<template>
  <Card title="Client-chat intents">
    <p class="text-sm mb-2 text-slate-700 dark:text-slate-300">
      When a client's message matches an intent, the assistant replies with that intent's pre-formed message.
    </p>
    <p class="text-sm mb-4 text-slate-700 dark:text-slate-300">
      Placeholders in double braces, like
      <code class="px-1 rounded bg-gray-100 dark:bg-slate-700">{{ slotToken('open_today') }}</code>,
      are filled from this shop's live data when a client asks.
    </p>

    <div v-if="fragments.length" class="mb-5">
      <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2">
        Available placeholders
      </p>
      <div class="space-y-2 text-sm">
        <div v-for="frag in fragments" :key="'ref-' + frag.name">
          <code class="px-1.5 py-0.5 rounded font-mono bg-gray-100 dark:bg-slate-700 dark:text-slate-100">{{ slotToken(frag.name) }}</code>
          <span class="block mt-1 text-slate-700 dark:text-slate-300 break-words">{{ frag.example ?? 'no data yet' }}</span>
        </div>
      </div>
    </div>

    <form @submit.prevent="saveEdit">
      <div class="grid grid-cols-12 gap-2 items-start">
        <!-- Header -->
        <div class="col-span-2"><span class="text-slate-700 dark:text-slate-300 text-xl">Name</span></div>
        <div class="col-span-3"><span class="text-slate-700 dark:text-slate-300 text-xl">When to use</span></div>
        <div class="col-span-4"><span class="text-slate-700 dark:text-slate-300 text-xl">Reply</span></div>
        <div class="col-span-1"><span class="text-slate-700 dark:text-slate-300 text-xl">On</span></div>
        <div class="col-span-2"/>

        <template v-for="intent in intents" :key="intent.id">
          <!-- Not editing: shown as plain, standard-colour text (not an input) -->
          <template v-if="editingId !== intent.id">
            <div class="col-span-2">
              <span class="text-slate-700 dark:text-slate-300">{{ displayName(intent.name) }}</span>
            </div>
            <div class="col-span-3">
              <span class="text-slate-700 dark:text-slate-300 break-words">{{ intent.whenToUse }}</span>
            </div>
            <div class="col-span-4">
              <span class="text-slate-700 dark:text-slate-300 break-words">{{ intent.replyTemplate }}</span>
            </div>
            <div class="col-span-1">
              <Switch name="intent_enabled" disabled v-model="intent.enabled"/>
            </div>
            <div class="col-span-2 grid grid-cols-2 gap-x-2">
              <div class="col-span-1">
                <Button v-if="$can('patchChatIntent')"
                        type="button"
                        class="btn-sm block-btn"
                        icon="heroicons-outline:pencil"
                        @click="startEdit(intent)"/>
              </div>
              <div class="col-span-1">
                <Button v-if="$can('deleteChatIntent')"
                        type="button"
                        btn-class="btn-danger"
                        class="btn-sm block-btn"
                        icon="heroicons-outline:trash"
                        @click="removeIntent(intent)"/>
              </div>
            </div>
          </template>

          <!-- Editing: the row becomes input fields -->
          <template v-if="editingId === intent.id">
            <div class="col-span-2">
              <TextInput type="text" name="edit_intent_name"
                         v-model="editDraft.name" placeholder="open_today"/>
            </div>
            <div class="col-span-3">
              <TextInput type="text" name="edit_intent_when_to_use"
                         v-model="editDraft.whenToUse" placeholder="when to classify as this"/>
            </div>
            <div class="col-span-4">
              <Textarea name="edit_intent_reply"
                        v-model="editDraft.replyTemplate" :rows="2"
                        placeholder="We're here today — {{open_today}}."/>
              <div class="flex flex-wrap gap-1 mt-1">
                <button v-for="frag in fragments" :key="frag.name" type="button"
                        class="px-1.5 py-0.5 text-xs rounded border border-gray-300 dark:border-slate-500 hover:text-primary-600"
                        :title="frag.description"
                        @click="insertFragment(frag.name, editDraft)">
                  {{ frag.name }}
                </button>
              </div>
              <p class="mt-1 text-sm" :class="previewReply(editDraft.replyTemplate).ok
                  ? 'text-slate-700 dark:text-slate-300'
                  : 'text-amber-600 dark:text-amber-400'">
                Preview: {{ previewReply(editDraft.replyTemplate).display }}
              </p>
            </div>
            <div class="col-span-1">
              <Switch name="edit_intent_enabled" active-class="bg-primary-500" v-model="editDraft.enabled"/>
            </div>
            <div class="col-span-2 grid grid-cols-2 gap-x-2">
              <div class="col-span-1">
                <Button type="submit" class="btn-sm block-btn" icon="heroicons-outline:check"/>
              </div>
              <div class="col-span-1">
                <Button type="button" class="btn-sm block-btn"
                        icon="heroicons-outline:x" @click="cancelEdit"/>
              </div>
            </div>
          </template>
        </template>

        <div v-if="intents.length === 0" class="col-span-12 text-slate-700 dark:text-slate-300">
          No intents yet — add one below.
        </div>
      </div>
    </form>

    <!-- Add new -->
    <form v-if="$can('postChatIntent')" @submit.prevent="addNew"
          class="mt-4 border-t border-gray-200 dark:border-slate-700 pt-4">
      <div class="grid grid-cols-12 gap-2 items-start">
        <div class="col-span-2">
          <TextInput type="text" name="new_intent_name"
                     v-model="newDraft.name" placeholder="open_today"/>
        </div>
        <div class="col-span-3">
          <TextInput type="text" name="new_intent_when_to_use"
                     v-model="newDraft.whenToUse" placeholder="when to classify as this"/>
        </div>
        <div class="col-span-4">
          <Textarea name="new_intent_reply"
                    v-model="newDraft.replyTemplate" :rows="2"
                    placeholder="We're here today — {{open_today}}."/>
          <div class="flex flex-wrap gap-1 mt-1">
            <button v-for="frag in fragments" :key="'new-' + frag.name" type="button"
                    class="px-1.5 py-0.5 text-xs rounded border border-gray-300 dark:border-slate-500 hover:text-primary-600"
                    :title="frag.description"
                    @click="insertFragment(frag.name, newDraft)">
              {{ frag.name }}
            </button>
          </div>
          <p class="mt-1 text-sm" :class="previewReply(newDraft.replyTemplate).ok
              ? 'text-slate-700 dark:text-slate-300'
              : 'text-amber-600 dark:text-amber-400'">
            Preview: {{ previewReply(newDraft.replyTemplate).display }}
          </p>
        </div>
        <div class="col-span-1">
          <Switch name="new_intent_enabled" active-class="bg-primary-500" v-model="newDraft.enabled"/>
        </div>
        <div class="col-span-2 flex justify-end">
          <Button type="submit" class="btn-sm block-btn" icon="heroicons-outline:plus"/>
        </div>
      </div>
    </form>
  </Card>
</template>

<style scoped lang="scss">
</style>
