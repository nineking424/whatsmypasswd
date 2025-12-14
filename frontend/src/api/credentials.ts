import { api } from './client'

export interface Credential {
  id: number
  name: string
  type: 'oracle' | 'linux' | 'ftp' | 's3'
  host?: string
  port?: number
  username?: string
  password?: string
  extra_data?: Record<string, unknown>
  category_id?: number
  category_name?: string
  category_color?: string
  tags: string[]
  description?: string
  created_at: string
  updated_at?: string
}

export interface CredentialListResponse {
  items: Credential[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface CredentialFilters {
  page?: number
  page_size?: number
  search?: string
  type?: string
  category_id?: number
}

export const credentialsApi = {
  list(filters: CredentialFilters = {}) {
    return api.get<CredentialListResponse>('/credentials', { params: filters })
  },

  get(id: number) {
    return api.get<Credential>(`/credentials/${id}`)
  },

  create(data: Partial<Credential>) {
    return api.post<Credential>('/credentials', data)
  },

  update(id: number, data: Partial<Credential>) {
    return api.put<Credential>(`/credentials/${id}`, data)
  },

  delete(id: number) {
    return api.delete(`/credentials/${id}`)
  },

  logCopy(id: number, field: string) {
    return api.post(`/credentials/${id}/copy`, null, { params: { field } })
  },
}
