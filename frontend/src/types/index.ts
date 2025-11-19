// API Types matching backend schemas

export type PostStatus = 'draft' | 'review' | 'approved' | 'scheduled' | 'published' | 'rejected'

export type MediaType = 'image' | 'video' | 'gallery'

export interface RedditPostData {
  reddit_post_id: string
  subreddit: string
  title: string
  content?: string
  url?: string
  author: string
  score: number
  num_comments: number
  upvote_ratio: number
  created_utc: number
  permalink: string
  flair?: string
  media_type?: MediaType
  media_urls: string[]
  top_comments?: Array<{
    author: string
    body: string
    score: number
  }>
}

export interface LinkedInContent {
  content: string
  quality_score?: number
  hashtags: string[]
  char_count?: number
}

export interface Post {
  id: string
  category: string
  reddit_data: RedditPostData
  linkedin_content?: LinkedInContent
  template_id?: string
  status: PostStatus
  scheduled_date?: string
  published_date?: string
  notion_page_id?: string
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export interface Category {
  id: string
  name: string
  description: string
  subreddits: string[]
  default_template: string
  hashtags: string[]
  filters: {
    min_score: number
    min_comments: number
    max_age_days: number
    exclude_nsfw: boolean
  }
  created_at: string
  updated_at: string
}

export interface Template {
  id: string
  name: string
  description: string
  system_prompt: string
  task_instruction: string
  requirements: string[]
  target_length: {
    min: number
    max: number
  }
  hashtag_count: {
    min: number
    max: number
  }
  style: {
    tone: string
    voice: string
    emoji_usage: string
  }
  examples: string[]
  created_at: string
  updated_at: string
}

export interface Job {
  job_id: string
  type: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  error?: string
  [key: string]: any
}

export interface Settings {
  app_name: string
  version: string
  reddit?: {
    rate_limit_rpm: number
    retry_attempts: number
  }
  gemini?: {
    model: string
    temperature: number
    max_tokens: number
  }
  notion?: {
    rate_limit_rps: number
  }
  storage?: {
    max_size_gb: number
    cleanup_days: number
  }
}

// API Request/Response types

export interface RedditFetchRequest {
  category: string
  time_filter?: 'hour' | 'day' | 'week' | 'month' | 'year'
  limit?: number
  min_score?: number
}

export interface ContentGenerationRequest {
  post_ids: string[]
  template_id?: string
  variations?: number
}

export interface NotionSyncRequest {
  post_ids: string[]
  update_existing?: boolean
}

export interface JobResponse {
  job_id: string
  status: string
  message: string
}

export interface MessageResponse {
  message: string
  detail?: string
}

export interface StatsResponse {
  categories: number
  templates: number
  posts: number
  posts_by_status: Record<string, number>
}

export interface HealthResponse {
  status: string
  version: string
  timestamp: string
}

// UI State types

export interface FilterState {
  category?: string
  status?: PostStatus
  search?: string
}
