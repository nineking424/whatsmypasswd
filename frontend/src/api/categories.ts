import { api } from './client'

export interface Category {
  id: number
  name: string
  color: string
  created_at: string
  updated_at?: string
  credential_count: number
}

export const categoriesApi = {
  list() {
    return api.get<Category[]>('/categories')
  },

  get(id: number) {
    return api.get<Category>(`/categories/${id}`)
  },

  create(data: { name: string; color?: string }) {
    return api.post<Category>('/categories', data)
  },

  update(id: number, data: { name?: string; color?: string }) {
    return api.put<Category>(`/categories/${id}`, data)
  },

  delete(id: number) {
    return api.delete(`/categories/${id}`)
  },
}
