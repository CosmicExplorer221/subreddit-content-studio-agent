import { create } from 'zustand'
import type { Template } from '@/types'
import * as api from '@/api/client'

interface TemplateState {
  templates: Template[]
  loading: boolean
  error: string | null

  // Actions
  fetchTemplates: () => Promise<void>
  getTemplate: (id: string) => Template | undefined
  createTemplate: (data: Partial<Template>) => Promise<void>
  updateTemplate: (id: string, data: Partial<Template>) => Promise<void>
  deleteTemplate: (id: string) => Promise<void>
}

export const useTemplateStore = create<TemplateState>((set, get) => ({
  templates: [],
  loading: false,
  error: null,

  fetchTemplates: async () => {
    set({ loading: true, error: null })
    try {
      const { data } = await api.listTemplates()
      set({ templates: data, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  getTemplate: (id: string) => {
    return get().templates.find((t) => t.id === id)
  },

  createTemplate: async (templateData: Partial<Template>) => {
    try {
      const { data } = await api.createTemplate(templateData)
      set((state) => ({
        templates: [...state.templates, data],
      }))
    } catch (error: any) {
      set({ error: error.message })
      throw error
    }
  },

  updateTemplate: async (id: string, updates: Partial<Template>) => {
    try {
      const { data } = await api.updateTemplate(id, updates)
      set((state) => ({
        templates: state.templates.map((t) => (t.id === id ? data : t)),
      }))
    } catch (error: any) {
      set({ error: error.message })
      throw error
    }
  },

  deleteTemplate: async (id: string) => {
    try {
      await api.deleteTemplate(id)
      set((state) => ({
        templates: state.templates.filter((t) => t.id !== id),
      }))
    } catch (error: any) {
      set({ error: error.message })
      throw error
    }
  },
}))
