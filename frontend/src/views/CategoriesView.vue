<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { categoriesApi, type Category } from '@/api/categories'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'

const router = useRouter()
const authStore = useAuthStore()

const categories = ref<Category[]>([])
const loading = ref(false)
const showForm = ref(false)
const editingId = ref<number | null>(null)

const form = ref({
  name: '',
  color: '#6366f1',
})

async function loadCategories() {
  loading.value = true
  try {
    const response = await categoriesApi.list()
    categories.value = response.data
  } catch (e) {
    console.error('Failed to load categories', e)
  } finally {
    loading.value = false
  }
}

function openForm(category?: Category) {
  if (category) {
    editingId.value = category.id
    form.value = { name: category.name, color: category.color }
  } else {
    editingId.value = null
    form.value = { name: '', color: '#6366f1' }
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingId.value = null
  form.value = { name: '', color: '#6366f1' }
}

async function handleSubmit() {
  if (!form.value.name) return

  try {
    if (editingId.value) {
      await categoriesApi.update(editingId.value, form.value)
    } else {
      await categoriesApi.create(form.value)
    }
    closeForm()
    await loadCategories()
  } catch (e) {
    console.error('Failed to save category', e)
  }
}

async function deleteCategory(id: number) {
  if (!confirm('Are you sure? Credentials in this category will become uncategorized.')) return

  try {
    await categoriesApi.delete(id)
    await loadCategories()
  } catch (e) {
    console.error('Failed to delete category', e)
  }
}

function logout() {
  authStore.logout()
  router.push('/login')
}

onMounted(loadCategories)
</script>

<template>
  <AppLayout>
    <template #header>
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">Categories</h1>
        <div class="flex items-center gap-4">
          <button
            @click="openForm()"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            + New Category
          </button>
          <button
            @click="logout"
            class="px-4 py-2 text-gray-600 hover:text-gray-900 transition"
          >
            Logout
          </button>
        </div>
      </div>
    </template>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent"></div>
    </div>

    <!-- Empty state -->
    <div v-else-if="categories.length === 0" class="text-center py-12 text-gray-500">
      No categories yet. Create your first one!
    </div>

    <!-- Categories list -->
    <div v-else class="grid gap-4 max-w-2xl">
      <div
        v-for="cat in categories"
        :key="cat.id"
        class="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm border"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-4 h-4 rounded-full"
            :style="{ backgroundColor: cat.color }"
          />
          <span class="font-medium">{{ cat.name }}</span>
          <span class="text-sm text-gray-500">
            ({{ cat.credential_count }} credential{{ cat.credential_count !== 1 ? 's' : '' }})
          </span>
        </div>

        <div class="flex gap-2">
          <button
            @click="openForm(cat)"
            class="p-2 text-gray-400 hover:text-gray-600 transition"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            @click="deleteCategory(cat.id)"
            class="p-2 text-gray-400 hover:text-red-600 transition"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Form Modal -->
    <div
      v-if="showForm"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeForm"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">
          {{ editingId ? 'Edit Category' : 'New Category' }}
        </h2>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Color</label>
            <div class="flex items-center gap-3">
              <input
                v-model="form.color"
                type="color"
                class="w-12 h-10 rounded cursor-pointer"
              />
              <input
                v-model="form.color"
                type="text"
                pattern="^#[0-9a-fA-F]{6}$"
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono"
              />
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="closeForm"
              class="px-4 py-2 text-gray-700 hover:text-gray-900 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
            >
              {{ editingId ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>
