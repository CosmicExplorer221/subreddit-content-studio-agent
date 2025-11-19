// API Client - Following frontend-developer.md patterns
import axios from 'axios'
import type { Post, GeneratedPost, Template, Category, APIKeysStatus } from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Posts
export const getPosts = async (category?: string) => {
  const { data } = await api.get<{ posts: Post[]; total: number }>('/posts', {
    params: { category, limit: 100 }
  })
  return data
}

export const getPost = async (id: string) => {
  const { data } = await api.get<Post>(`/posts/${id}`)
  return data
}

// Templates
export const getTemplates = async (category?: string) => {
  const { data } = await api.get<{ templates: Template[]; total: number }>('/templates', {
    params: { category }
  })
  return data
}

// Categories
export const getCategories = async () => {
  const { data } = await api.get<{ categories: Category[]; total: number }>('/categories')
  return data
}

// Generation
export const generateContent = async (postIds: string[], templateId: string, variations: number = 1) => {
  const { data } = await api.post('/generate', {
    post_ids: postIds,
    template_id: templateId,
    variations
  })
  return data
}

export const getGeneratedPosts = async () => {
  const { data } = await api.get<GeneratedPost[]>('/generate/posts')
  return data
}

export const deleteGeneratedPost = async (id: string) => {
  await api.delete(`/generate/posts/${id}`)
}

export const updateGeneratedPost = async (id: string, updates: any) => {
  const { data } = await api.put(`/generate/posts/${id}`, updates)
  return data
}

// Notion
export const syncToNotion = async (generatedPostIds: string[], updateExisting: boolean = false) => {
  const { data } = await api.post('/notion/sync', {
    generated_post_ids: generatedPostIds,
    update_existing: updateExisting
  })
  return data
}

// Settings
export const getAPIKeysStatus = async () => {
  const { data} = await api.get<APIKeysStatus>('/settings/api-keys')
  return data
}

export const updateSettings = async (settings: any) => {
  const { data } = await api.put('/settings', settings)
  return data
}

export default api
