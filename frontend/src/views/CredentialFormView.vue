<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { credentialsApi, type Credential } from '@/api/credentials'
import { categoriesApi, type Category } from '@/api/categories'
import AppLayout from '@/components/AppLayout.vue'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const categories = ref<Category[]>([])

const form = ref({
  name: '',
  type: 'linux' as 'oracle' | 'linux' | 'ftp' | 's3',
  host: '',
  port: undefined as number | undefined,
  username: '',
  password: '',
  category_id: undefined as number | undefined,
  tags: [] as string[],
  description: '',
  extra_data: {} as Record<string, unknown>,
})

const tagInput = ref('')

const defaultPorts: Record<string, number> = {
  oracle: 1521,
  linux: 22,
  ftp: 21,
  s3: 443,
}

function onTypeChange() {
  form.value.port = defaultPorts[form.value.type]
  form.value.extra_data = {}
}

function addTag() {
  const tag = tagInput.value.trim()
  if (tag && !form.value.tags.includes(tag)) {
    form.value.tags.push(tag)
  }
  tagInput.value = ''
}

function removeTag(tag: string) {
  form.value.tags = form.value.tags.filter(t => t !== tag)
}

async function loadCredential() {
  if (!isEdit.value) return

  loading.value = true
  try {
    const response = await credentialsApi.get(Number(route.params.id))
    const cred = response.data
    form.value = {
      name: cred.name,
      type: cred.type,
      host: cred.host || '',
      port: cred.port,
      username: cred.username || '',
      password: cred.password || '',
      category_id: cred.category_id,
      tags: cred.tags || [],
      description: cred.description || '',
      extra_data: cred.extra_data || {},
    }
  } catch (e) {
    error.value = 'Failed to load credential'
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const response = await categoriesApi.list()
    categories.value = response.data
  } catch (e) {
    console.error('Failed to load categories', e)
  }
}

async function handleSubmit() {
  if (!form.value.name) {
    error.value = 'Name is required'
    return
  }

  saving.value = true
  error.value = ''

  try {
    const data: Partial<Credential> = {
      ...form.value,
      port: form.value.port || undefined,
      category_id: form.value.category_id || undefined,
    }

    if (isEdit.value) {
      await credentialsApi.update(Number(route.params.id), data)
    } else {
      await credentialsApi.create(data)
    }

    router.push('/')
  } catch (e) {
    error.value = 'Failed to save credential'
    console.error(e)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadCredential()
})
</script>

<template>
  <AppLayout>
    <template #header>
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">
          {{ isEdit ? 'Edit Credential' : 'New Credential' }}
        </h1>
        <router-link
          to="/"
          class="px-4 py-2 text-gray-600 hover:text-gray-900 transition"
        >
          Cancel
        </router-link>
      </div>
    </template>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent"></div>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="max-w-2xl space-y-6">
      <!-- Error -->
      <div v-if="error" class="p-4 bg-red-50 text-red-600 rounded-lg">
        {{ error }}
      </div>

      <!-- Name -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
        <input
          v-model="form.name"
          type="text"
          required
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="My Database Server"
        />
      </div>

      <!-- Type -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Type *</label>
        <select
          v-model="form.type"
          @change="onTypeChange"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option value="oracle">Oracle DB</option>
          <option value="linux">Linux Server</option>
          <option value="ftp">FTP</option>
          <option value="s3">S3</option>
        </select>
      </div>

      <!-- Host & Port -->
      <div class="grid grid-cols-3 gap-4">
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Host</label>
          <input
            v-model="form.host"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="192.168.1.100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Port</label>
          <input
            v-model.number="form.port"
            type="number"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </div>

      <!-- Username & Password -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input
            v-model="form.username"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </div>

      <!-- Oracle specific: Service Name, TNS -->
      <template v-if="form.type === 'oracle'">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Service Name</label>
          <input
            v-model="form.extra_data.service_name"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="ORCL"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">TNS Entry</label>
          <textarea
            v-model="form.extra_data.tns"
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
            placeholder="(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)...))"
          />
        </div>
      </template>

      <!-- S3 specific -->
      <template v-if="form.type === 's3'">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Endpoint</label>
            <input
              v-model="form.extra_data.endpoint"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="s3.amazonaws.com"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Region</label>
            <input
              v-model="form.extra_data.region"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="ap-northeast-2"
            />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Access Key</label>
            <input
              v-model="form.extra_data.access_key"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Secret Key</label>
            <input
              v-model="form.extra_data.secret_key"
              type="password"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Bucket</label>
          <input
            v-model="form.extra_data.bucket"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </template>

      <!-- Category -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
        <select
          v-model="form.category_id"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option :value="undefined">No Category</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>

      <!-- Tags -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Tags</label>
        <div class="flex gap-2 mb-2">
          <input
            v-model="tagInput"
            type="text"
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Add a tag..."
            @keyup.enter.prevent="addTag"
          />
          <button
            type="button"
            @click="addTag"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
          >
            Add
          </button>
        </div>
        <div v-if="form.tags.length" class="flex flex-wrap gap-2">
          <span
            v-for="tag in form.tags"
            :key="tag"
            class="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm flex items-center gap-1"
          >
            {{ tag }}
            <button type="button" @click="removeTag(tag)" class="hover:text-indigo-900">
              &times;
            </button>
          </span>
        </div>
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          v-model="form.description"
          rows="3"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Optional description..."
        />
      </div>

      <!-- Submit -->
      <div class="flex justify-end gap-4">
        <router-link
          to="/"
          class="px-6 py-2 text-gray-700 hover:text-gray-900 transition"
        >
          Cancel
        </router-link>
        <button
          type="submit"
          :disabled="saving"
          class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ saving ? 'Saving...' : (isEdit ? 'Update' : 'Create') }}
        </button>
      </div>
    </form>
  </AppLayout>
</template>
