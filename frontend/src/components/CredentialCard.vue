<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { credentialsApi, type Credential } from '@/api/credentials'

const props = defineProps<{
  credential: Credential
}>()

const emit = defineEmits<{
  delete: [id: number]
}>()

const router = useRouter()
const showPassword = ref(false)
const copied = ref<string | null>(null)

const typeLabels: Record<string, string> = {
  oracle: 'Oracle DB',
  linux: 'Linux Server',
  ftp: 'FTP',
  s3: 'S3',
}

const typeColors: Record<string, string> = {
  oracle: 'bg-red-100 text-red-800',
  linux: 'bg-green-100 text-green-800',
  ftp: 'bg-blue-100 text-blue-800',
  s3: 'bg-yellow-100 text-yellow-800',
}

async function copyToClipboard(field: string, value: string | undefined) {
  if (!value) return

  try {
    await navigator.clipboard.writeText(value)
    copied.value = field
    setTimeout(() => { copied.value = null }, 2000)

    // Log copy action
    await credentialsApi.logCopy(props.credential.id, field)
  } catch (e) {
    console.error('Failed to copy', e)
  }
}

function editCredential() {
  router.push(`/credentials/${props.credential.id}/edit`)
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition">
    <!-- Header -->
    <div class="flex items-start justify-between mb-3">
      <div>
        <h3 class="font-semibold text-gray-900">{{ credential.name }}</h3>
        <div class="flex items-center gap-2 mt-1">
          <span :class="['px-2 py-0.5 text-xs rounded-full', typeColors[credential.type]]">
            {{ typeLabels[credential.type] }}
          </span>
          <span
            v-if="credential.category_name"
            class="px-2 py-0.5 text-xs rounded-full"
            :style="{ backgroundColor: credential.category_color + '20', color: credential.category_color }"
          >
            {{ credential.category_name }}
          </span>
        </div>
      </div>

      <div class="flex gap-1">
        <button
          @click="editCredential"
          class="p-1.5 text-gray-400 hover:text-gray-600 transition"
          title="Edit"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          @click="emit('delete', credential.id)"
          class="p-1.5 text-gray-400 hover:text-red-600 transition"
          title="Delete"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Connection info -->
    <div class="space-y-2 text-sm">
      <div v-if="credential.host" class="flex items-center justify-between">
        <span class="text-gray-500">Host:</span>
        <div class="flex items-center gap-2">
          <span class="font-mono">{{ credential.host }}{{ credential.port ? `:${credential.port}` : '' }}</span>
          <button
            @click="copyToClipboard('host', credential.host)"
            :class="['text-gray-400 hover:text-indigo-600 transition', copied === 'host' ? 'text-green-600' : '']"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
        </div>
      </div>

      <div v-if="credential.username" class="flex items-center justify-between">
        <span class="text-gray-500">Username:</span>
        <div class="flex items-center gap-2">
          <span class="font-mono">{{ credential.username }}</span>
          <button
            @click="copyToClipboard('username', credential.username)"
            :class="['text-gray-400 hover:text-indigo-600 transition', copied === 'username' ? 'text-green-600' : '']"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
        </div>
      </div>

      <div v-if="credential.password" class="flex items-center justify-between">
        <span class="text-gray-500">Password:</span>
        <div class="flex items-center gap-2">
          <span class="font-mono">{{ showPassword ? credential.password : '••••••••' }}</span>
          <button
            @click="showPassword = !showPassword"
            class="text-gray-400 hover:text-gray-600 transition"
          >
            <svg v-if="showPassword" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </button>
          <button
            @click="copyToClipboard('password', credential.password)"
            :class="['text-gray-400 hover:text-indigo-600 transition', copied === 'password' ? 'text-green-600' : '']"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Description -->
    <p v-if="credential.description" class="mt-3 text-sm text-gray-500 line-clamp-2">
      {{ credential.description }}
    </p>

    <!-- Tags -->
    <div v-if="credential.tags?.length" class="mt-3 flex flex-wrap gap-1">
      <span
        v-for="tag in credential.tags"
        :key="tag"
        class="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
      >
        {{ tag }}
      </span>
    </div>
  </div>
</template>
