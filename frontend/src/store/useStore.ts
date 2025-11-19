// Zustand Store - Following frontend-developer.md patterns
import { create } from 'zustand'
import type { Post, GeneratedPost, Template } from '../types'
import * as api from '../api/client'

interface AppState {
  // Data
  posts: Post[]
  generatedPosts: GeneratedPost[]
  templates: Template[]
  selectedPostIds: Set<string>
  selectedGenPostIds: Set<string>

  // UI State
  loading: boolean
  error: string | null

  // Actions
  loadPosts: () => Promise<void>
  loadGeneratedPosts: () => Promise<void>
  loadTemplates: () => Promise<void>
  togglePostSelection: (id: string) => void
  toggleGenPostSelection: (id: string) => void
  clearSelections: () => void
  generateContent: (templateId: string) => Promise<void>
  syncToNotion: () => Promise<void>
  deleteGeneratedPost: (id: string) => Promise<void>
}

export const useStore = create<AppState>((set, get) => ({
  posts: [],
  generatedPosts: [],
  templates: [],
  selectedPostIds: new Set(),
  selectedGenPostIds: new Set(),
  loading: false,
  error: null,

  loadPosts: async () => {
    set({ loading: true, error: null })
    try {
      const data = await api.getPosts('railway')
      set({ posts: data.posts, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  loadGeneratedPosts: async () => {
    set({ loading: true, error: null })
    try {
      const posts = await api.getGeneratedPosts()
      set({ generatedPosts: posts, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  loadTemplates: async () => {
    try {
      const data = await api.getTemplates('railway')
      set({ templates: data.templates })
    } catch (error: any) {
      set({ error: error.message })
    }
  },

  togglePostSelection: (id: string) => {
    const selected = new Set(get().selectedPostIds)
    if (selected.has(id)) {
      selected.delete(id)
    } else {
      selected.add(id)
    }
    set({ selectedPostIds: selected })
  },

  toggleGenPostSelection: (id: string) => {
    const selected = new Set(get().selectedGenPostIds)
    if (selected.has(id)) {
      selected.delete(id)
    } else {
      selected.add(id)
    }
    set({ selectedGenPostIds: selected })
  },

  clearSelections: () => {
    set({ selectedPostIds: new Set(), selectedGenPostIds: new Set() })
  },

  generateContent: async (templateId: string) => {
    const postIds = Array.from(get().selectedPostIds)
    if (postIds.length === 0) return

    set({ loading: true, error: null })
    try {
      await api.generateContent(postIds, templateId)
      await get().loadGeneratedPosts()
      set({ loading: false, selectedPostIds: new Set() })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  syncToNotion: async () => {
    const postIds = Array.from(get().selectedGenPostIds)
    if (postIds.length === 0) return

    set({ loading: true, error: null })
    try {
      await api.syncToNotion(postIds)
      await get().loadGeneratedPosts()
      set({ loading: false, selectedGenPostIds: new Set() })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  deleteGeneratedPost: async (id: string) => {
    try {
      await api.deleteGeneratedPost(id)
      await get().loadGeneratedPosts()
    } catch (error: any) {
      set({ error: error.message })
    }
  }
}))
