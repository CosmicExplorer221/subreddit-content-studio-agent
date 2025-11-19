import { create } from 'zustand'
import type { Category } from '@/types'
import * as api from '@/api/client'

interface CategoryState {
  categories: Category[]
  loading: boolean
  error: string | null

  // Actions
  fetchCategories: () => Promise<void>
  getCategory: (id: string) => Category | undefined
  createCategory: (data: Partial<Category>) => Promise<void>
  updateCategory: (id: string, data: Partial<Category>) => Promise<void>
  deleteCategory: (id: string) => Promise<void>
}

export const useCategoryStore = create<CategoryState>((set, get) => ({
  categories: [],
  loading: false,
  error: null,

  fetchCategories: async () => {
    set({ loading: true, error: null })
    try {
      const { data } = await api.listCategories()
      set({ categories: data, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  getCategory: (id: string) => {
    return get().categories.find((c) => c.id === id)
  },

  createCategory: async (categoryData: Partial<Category>) => {
    try {
      const { data } = await api.createCategory(categoryData)
      set((state) => ({
        categories: [...state.categories, data],
      }))
    } catch (error: any) {
      set({ error: error.message })
      throw error
    }
  },

  updateCategory: async (id: string, updates: Partial<Category>) => {
    try {
      const { data } = await api.updateCategory(id, updates)
      set((state) => ({
        categories: state.categories.map((c) => (c.id === id ? data : c)),
      }))
    } catch (error: any) {
      set({ error: error.message })
      throw error
    }
  },

  deleteCategory: async (id: string) => {
    try {
      await api.deleteCategory(id)
      set((state) => ({
        categories: state.categories.filter((c) => c.id !== id),
      }))
    } catch (error: any) {
      set({ error: error.message })
      throw error
    }
  },
}))
