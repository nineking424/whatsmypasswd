<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'

const router = useRouter()
const authStore = useAuthStore()

interface AuditLog {
  id: number
  credential_id?: number
  credential_name?: string
  action: string
  ip_address?: string
  user_agent?: string
  created_at: string
}

interface AuditLogListResponse {
  items: AuditLog[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

const logs = ref<AuditLog[]>([])
const loading = ref(false)
const page = ref(1)
const totalPages = ref(1)
const actionFilter = ref('')

const actionLabels: Record<string, { label: string; color: string }> = {
  view: { label: 'View', color: 'bg-blue-100 text-blue-800' },
  copy: { label: 'Copy', color: 'bg-purple-100 text-purple-800' },
  create: { label: 'Create', color: 'bg-green-100 text-green-800' },
  update: { label: 'Update', color: 'bg-yellow-100 text-yellow-800' },
  delete: { label: 'Delete', color: 'bg-red-100 text-red-800' },
}

async function loadLogs() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: 50 }
    if (actionFilter.value) params.action = actionFilter.value

    const response = await api.get<AuditLogListResponse>('/audit-logs', { params })
    logs.value = response.data.items
    totalPages.value = response.data.total_pages
  } catch (e) {
    console.error('Failed to load audit logs', e)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString()
}

function handleFilterChange() {
  page.value = 1
  loadLogs()
}

function handlePageChange(newPage: number) {
  page.value = newPage
  loadLogs()
}

function logout() {
  authStore.logout()
  router.push('/login')
}

onMounted(loadLogs)
</script>

<template>
  <AppLayout>
    <template #header>
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">Audit Logs</h1>
        <button
          @click="logout"
          class="px-4 py-2 text-gray-600 hover:text-gray-900 transition"
        >
          Logout
        </button>
      </div>
    </template>

    <!-- Filters -->
    <div class="mb-6">
      <select
        v-model="actionFilter"
        @change="handleFilterChange"
        class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
      >
        <option value="">All Actions</option>
        <option value="view">View</option>
        <option value="copy">Copy</option>
        <option value="create">Create</option>
        <option value="update">Update</option>
        <option value="delete">Delete</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent"></div>
    </div>

    <!-- Empty state -->
    <div v-else-if="logs.length === 0" class="text-center py-12 text-gray-500">
      No audit logs found.
    </div>

    <!-- Logs table -->
    <div v-else class="bg-white rounded-lg shadow-sm border overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Time</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Action</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Credential</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">IP Address</th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 text-sm text-gray-600">
              {{ formatDate(log.created_at) }}
            </td>
            <td class="px-4 py-3">
              <span :class="['px-2 py-1 text-xs rounded-full', actionLabels[log.action]?.color || 'bg-gray-100 text-gray-800']">
                {{ actionLabels[log.action]?.label || log.action }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm">
              {{ log.credential_name || '-' }}
            </td>
            <td class="px-4 py-3 text-sm text-gray-500 font-mono">
              {{ log.ip_address || '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-6 flex justify-center gap-2">
      <button
        v-for="p in totalPages"
        :key="p"
        @click="handlePageChange(p)"
        :class="[
          'px-3 py-1 rounded',
          p === page
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        {{ p }}
      </button>
    </div>
  </AppLayout>
</template>
