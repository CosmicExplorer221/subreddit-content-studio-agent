import { create } from 'zustand'
import type { Post, PostStatus } from '@/types'
import * as api from '@/api/client'

interface PostState {
  posts: Post[]
  selectedPosts: Set<string>
  loading: boolean
  error: string | null
  filters: {
    category?: string
    status?: PostStatus
    search?: string
  }

  // Actions
  fetchPosts: () => Promise<void>
  getPost: (id: string) => Promise<Post | null>
  updatePost: (id: string, data: Partial<Post>) => Promise<void>
  deletePost: (id: string) => Promise<void>
  toggleSelectPost: (id: string) => void
  selectAllPosts: () => void
  clearSelection: () => void
  setFilters: (filters: Partial<PostState['filters']>) => void
  clearFilters: () => void
}

export const usePostStore = create<PostState>((set, get) => ({
  posts: [],
  selectedPosts: new Set(),
  loading: false,
  error: null,
  filters: {},

  fetchPosts: async () => {
    set({ loading: true, error: null })
    try {
      const { filters } = get()
      const { data } = await api.listPosts({
        category: filters.category,
        status: filters.status,
        limit: 100,
      })

      // Apply search filter client-side
      let filteredPosts = data
      if (filters.search) {
        const search = filters.search.toLowerCase()
        filteredPosts = data.filter(
          (post) =>
            post.reddit_data.title.toLowerCase().includes(search) ||
            post.reddit_data.subreddit.toLowerCase().includes(search) ||
            post.category.toLowerCase().includes(search)
        )
      }

      set({ posts: filteredPosts, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  getPost: async (id: string) => {
    try {
      const { data } = await api.getPost(id)
      return data
    } catch (error) {
      return null
    }
  },

  updatePost: async (id: string, updates: Partial<Post>) => {
    try {
      const { data } = await api.updatePost(id, updates)
      set((state) => ({
        posts: state.posts.map((p) => (p.id === id ? data : p)),
      }))
    } catch (error: any) {
      set({ error: error.message })
    }
  },

  deletePost: async (id: string) => {
    try {
      await api.deletePost(id)
      set((state) => ({
        posts: state.posts.filter((p) => p.id !== id),
        selectedPosts: new Set(
          Array.from(state.selectedPosts).filter((pid) => pid !== id)
        ),
      }))
    } catch (error: any) {
      set({ error: error.message })
    }
  },

  toggleSelectPost: (id: string) => {
    set((state) => {
      const newSelection = new Set(state.selectedPosts)
      if (newSelection.has(id)) {
        newSelection.delete(id)
      } else {
        newSelection.add(id)
      }
      return { selectedPosts: newSelection }
    })
  },

  selectAllPosts: () => {
    set((state) => ({
      selectedPosts: new Set(state.posts.map((p) => p.id)),
    }))
  },

  clearSelection: () => {
    set({ selectedPosts: new Set() })
  },

  setFilters: (filters: Partial<PostState['filters']>) => {
    set((state) => ({
      filters: { ...state.filters, ...filters },
    }))
    get().fetchPosts()
  },

  clearFilters: () => {
    set({ filters: {} })
    get().fetchPosts()
  },
}))
