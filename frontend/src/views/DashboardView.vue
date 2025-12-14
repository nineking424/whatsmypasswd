<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { credentialsApi, type Credential, type CredentialFilters } from '@/api/credentials'
import { categoriesApi, type Category } from '@/api/categories'
import { useAuthStore } from '@/stores/auth'
import CredentialCard from '@/components/CredentialCard.vue'
import AppLayout from '@/components/AppLayout.vue'

const router = useRouter()
const authStore = useAuthStore()

const credentials = ref<Credential[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const error = ref('')

// Filters
const filters = ref<CredentialFilters>({
  page: 1,
  page_size: 20,
  search: '',
  type: '',
  category_id: undefined,
})

const totalPages = ref(1)
const total = ref(0)

async function loadCredentials() {
  loading.value = true
  error.value = ''

  try {
    const cleanFilters = { ...filters.value }
    if (!cleanFilters.search) delete cleanFilters.search
    if (!cleanFilters.type) delete cleanFilters.type
    if (!cleanFilters.category_id) delete cleanFilters.category_id

    const response = await credentialsApi.list(cleanFilters)
    credentials.value = response.data.items
    totalPages.value = response.data.total_pages
    total.value = response.data.total
  } catch (e) {
    error.value = 'Failed to load credentials'
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

async function deleteCredential(id: number) {
  if (!confirm('Are you sure you want to delete this credential?')) return

  try {
    await credentialsApi.delete(id)
    await loadCredentials()
  } catch (e) {
    console.error('Failed to delete credential', e)
  }
}

function handleSearch() {
  filters.value.page = 1
  loadCredentials()
}

function handlePageChange(page: number) {
  filters.value.page = page
  loadCredentials()
}

function logout() {
  authStore.logout()
  router.push('/login')
}

watch(() => filters.value.type, () => handleSearch())
watch(() => filters.value.category_id, () => handleSearch())

onMounted(() => {
  loadCredentials()
  loadCategories()
})
</script>

<template>
  <AppLayout>
    <template #header>
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">Credentials</h1>
        <div class="flex items-center gap-4">
          <router-link
            to="/credentials/new"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            + New
          </router-link>
          <button
            @click="logout"
            class="px-4 py-2 text-gray-600 hover:text-gray-900 transition"
          >
            Logout
          </button>
        </div>
      </div>
    </template>

    <!-- Filters -->
    <div class="mb-6 flex flex-wrap gap-4">
      <div class="flex-1 min-w-[200px]">
        <input
          v-model="filters.search"
          type="text"
          placeholder="Search by name or description..."
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          @keyup.enter="handleSearch"
        />
      </div>

      <select
        v-model="filters.type"
        class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
      >
        <option value="">All Types</option>
        <option value="oracle">Oracle DB</option>
        <option value="linux">Linux Server</option>
        <option value="ftp">FTP</option>
        <option value="s3">S3</option>
      </select>

      <select
        v-model="filters.category_id"
        class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
      >
        <option :value="undefined">All Categories</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>

      <button
        @click="handleSearch"
        class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
      >
        Search
      </button>
    </div>

    <!-- Results count -->
    <div class="mb-4 text-sm text-gray-600">
      {{ total }} credential(s) found
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-12 text-red-600">
      {{ error }}
    </div>

    <!-- Empty state -->
    <div v-else-if="credentials.length === 0" class="text-center py-12 text-gray-500">
      No credentials found. Create your first one!
    </div>

    <!-- Credentials grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <CredentialCard
        v-for="cred in credentials"
        :key="cred.id"
        :credential="cred"
        @delete="deleteCredential"
      />
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-6 flex justify-center gap-2">
      <button
        v-for="page in totalPages"
        :key="page"
        @click="handlePageChange(page)"
        :class="[
          'px-3 py-1 rounded',
          page === filters.page
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        {{ page }}
      </button>
    </div>
  </AppLayout>
</template>
