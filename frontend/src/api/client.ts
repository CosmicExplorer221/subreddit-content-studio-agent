import axios from 'axios'
import type {
  Post,
  Category,
  Template,
  Job,
  Settings,
  StatsResponse,
  HealthResponse,
  RedditFetchRequest,
  ContentGenerationRequest,
  NotionSyncRequest,
  JobResponse,
  MessageResponse,
} from '@/types'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health & Info
export const getHealth = () => api.get<HealthResponse>('/health')

// Posts
export const listPosts = (params?: {
  category?: string
  status?: string
  limit?: number
}) => api.get<Post[]>('/posts', { params })

export const getPost = (id: string) => api.get<Post>(`/posts/${id}`)

export const createPost = (data: Partial<Post>) => api.post<Post>('/posts', data)

export const updatePost = (id: string, data: Partial<Post>) =>
  api.put<Post>(`/posts/${id}`, data)

export const deletePost = (id: string) =>
  api.delete<MessageResponse>(`/posts/${id}`)

export const getPostsStats = () =>
  api.get<{
    total_posts: number
    by_status: Record<string, number>
    by_category: Record<string, number>
  }>('/posts/stats/summary')

export const generateContent = (data: ContentGenerationRequest) =>
  api.post<JobResponse>('/posts/generate', data)

// Categories
export const listCategories = () => api.get<Category[]>('/config/categories')

export const getCategory = (id: string) =>
  api.get<Category>(`/config/categories/${id}`)

export const createCategory = (data: Partial<Category>) =>
  api.post<Category>('/config/categories', data)

export const updateCategory = (id: string, data: Partial<Category>) =>
  api.put<Category>(`/config/categories/${id}`, data)

export const deleteCategory = (id: string) =>
  api.delete<MessageResponse>(`/config/categories/${id}`)

// Templates
export const listTemplates = () => api.get<Template[]>('/config/templates')

export const getTemplate = (id: string) =>
  api.get<Template>(`/config/templates/${id}`)

export const createTemplate = (data: Partial<Template>) =>
  api.post<Template>('/config/templates', data)

export const updateTemplate = (id: string, data: Partial<Template>) =>
  api.put<Template>(`/config/templates/${id}`, data)

export const deleteTemplate = (id: string) =>
  api.delete<MessageResponse>(`/config/templates/${id}`)

// Settings
export const getSettings = () => api.get<Settings>('/config/settings')

export const updateSettings = (data: Partial<Settings>) =>
  api.put<Settings>('/config/settings', data)

export const getStats = () => api.get<StatsResponse>('/config/stats')

// Reddit
export const fetchRedditPosts = (
  data: RedditFetchRequest,
  downloadMedia: boolean = true
) =>
  api.post<JobResponse>('/reddit/fetch', data, {
    params: { download_media: downloadMedia },
  })

export const getRedditStatus = () =>
  api.get<{
    status: string
    configured: boolean
    message?: string
  }>('/reddit/status')

export const getCategorySubreddits = (categoryId: string) =>
  api.get<{ category: string; subreddits: string[] }>(
    `/reddit/categories/${categoryId}/subreddits`
  )

// Media
export const downloadMedia = (data: {
  post_id: string
  urls: string[]
  category: string
}) => api.post<JobResponse>('/media/download', data)

export const getPostMedia = (redditPostId: string) =>
  api.get<{
    reddit_post_id: string
    media_files: Array<{
      type: string
      path: string
      url: string
      size: number
    }>
  }>(`/media/posts/${redditPostId}`)

export const getMediaStatus = () =>
  api.get<{
    status: string
    total_files: number
    total_size_mb: number
    categories: Record<string, number>
  }>('/media/status')

// Notion
export const syncToNotion = (data: NotionSyncRequest) =>
  api.post<JobResponse>('/notion/sync', data)

export const getNotionPostStatus = (postId: string) =>
  api.get<{
    post_id: string
    synced: boolean
    notion_page_id?: string
    message: string
  }>(`/notion/posts/${postId}/status`)

export const updateNotionStatus = (postId: string, status: string) =>
  api.put<MessageResponse>(`/notion/posts/${postId}/update-status`, { status })

export const getNotionStatus = () =>
  api.get<{
    status: string
    database_id?: string
    title?: string
    message?: string
  }>('/notion/status')

// Jobs
export const getJob = (jobId: string) => api.get<Job>(`/reddit/jobs/${jobId}`)

// Poll job until completion
export const pollJob = async (
  jobId: string,
  onProgress?: (job: Job) => void,
  maxWaitSeconds: number = 120
): Promise<Job> => {
  const startTime = Date.now()
  const pollInterval = 1000 // 1 second

  while (true) {
    const elapsed = (Date.now() - startTime) / 1000

    if (elapsed > maxWaitSeconds) {
      throw new Error('Job timeout exceeded')
    }

    const { data: job } = await getJob(jobId)

    if (onProgress) {
      onProgress(job)
    }

    if (job.status === 'completed' || job.status === 'failed') {
      return job
    }

    await new Promise((resolve) => setTimeout(resolve, pollInterval))
  }
}

export default api
