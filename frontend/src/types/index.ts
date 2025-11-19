// Type definitions matching backend schemas

export interface Comment {
  author: string
  body: string
  score: number
}

export interface Post {
  id: string
  title: string
  content: string
  category: string
  score: number
  num_comments: number
  author: string
  created_utc: number
  has_media: boolean
  media_type?: string
  media_url?: string
  top_comments: Comment[]
}

export interface GeneratedContent {
  id: string
  source_post_id: string
  content: string
  template_id: string
  quality_score: number
  hashtags: string[]
  generated_at: string
  variation_number: number
}

export interface GeneratedPost {
  id: string
  source_post: Post
  generated_content: GeneratedContent
  status: 'draft' | 'review' | 'approved' | 'published'
  notion_page_id?: string
  notion_synced_at?: string
}

export interface Template {
  id: string
  name: string
  description: string
  category: string
  system_prompt: string
  task_instruction: string
  requirements: {
    target_length: { min: number; max: number }
    hashtag_count: { min: number; max: number }
    tone: string
    include_call_to_action: boolean
    structure: string
  }
  example_hashtags: string[]
}

export interface Category {
  id: string
  name: string
  description: string
  default_template: string
  hashtags: string[]
  color: string
}

export interface APIKeysStatus {
  gemini_configured: boolean
  notion_configured: boolean
  notion_database_configured: boolean
}
