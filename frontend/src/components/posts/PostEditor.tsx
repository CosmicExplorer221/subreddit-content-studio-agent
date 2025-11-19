import { useState, useEffect } from 'react'
import { Save, X, ExternalLink } from 'lucide-react'
import type { Post, PostStatus } from '@/types'
import { usePostStore } from '@/store/usePostStore'

interface PostEditorProps {
  post: Post
  open: boolean
  onClose: () => void
}

const PostEditor = ({ post, open, onClose }: PostEditorProps) => {
  const { updatePost } = usePostStore()
  const [content, setContent] = useState(post.linkedin_content?.content || '')
  const [status, setStatus] = useState<PostStatus>(post.status)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setContent(post.linkedin_content?.content || '')
    setStatus(post.status)
  }, [post])

  const handleSave = async () => {
    setSaving(true)
    try {
      await updatePost(post.id, {
        linkedin_content: {
          ...post.linkedin_content,
          content,
          hashtags: extractHashtags(content),
          char_count: content.length,
        } as any,
        status,
      })
      onClose()
    } catch (error) {
      console.error('Failed to save post:', error)
    } finally {
      setSaving(false)
    }
  }

  const extractHashtags = (text: string) => {
    const matches = text.match(/#(\w+)/g)
    return matches ? matches.map((tag) => tag.substring(1)) : []
  }

  if (!open) return null

  const charCount = content.length
  const hashtags = extractHashtags(content)
  const qualityScore = post.linkedin_content?.quality_score || 0

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Edit Post</h2>
            <p className="text-sm text-gray-600 mt-1">
              {post.reddit_data.title}
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Left Column - Editor */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  LinkedIn Content
                </label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={20}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                  placeholder="Write or paste your LinkedIn content here..."
                />
                <div className="flex items-center justify-between mt-2 text-xs text-gray-600">
                  <span>
                    {charCount} characters | {hashtags.length} hashtags
                  </span>
                  {qualityScore > 0 && (
                    <span className="font-medium">
                      Quality: {qualityScore}/100
                    </span>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value as PostStatus)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="draft">Draft</option>
                  <option value="review">In Review</option>
                  <option value="approved">Approved</option>
                  <option value="scheduled">Scheduled</option>
                  <option value="published">Published</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
            </div>

            {/* Right Column - Original Reddit Post */}
            <div className="bg-gray-50 rounded-lg p-4 space-y-4">
              <h3 className="font-medium text-gray-900">Original Reddit Post</h3>

              <div>
                <p className="text-sm text-gray-600 mb-1">
                  r/{post.reddit_data.subreddit}
                </p>
                <h4 className="font-medium text-gray-900">
                  {post.reddit_data.title}
                </h4>
                <a
                  href={`https://reddit.com${post.reddit_data.permalink}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 mt-2"
                >
                  View on Reddit
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              {post.reddit_data.content && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Content</p>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">
                    {post.reddit_data.content}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Score</p>
                  <p className="font-medium text-gray-900">
                    {post.reddit_data.score.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Comments</p>
                  <p className="font-medium text-gray-900">
                    {post.reddit_data.num_comments.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Upvote Ratio</p>
                  <p className="font-medium text-gray-900">
                    {Math.round(post.reddit_data.upvote_ratio * 100)}%
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Author</p>
                  <p className="font-medium text-gray-900">
                    u/{post.reddit_data.author}
                  </p>
                </div>
              </div>

              {post.reddit_data.top_comments && post.reddit_data.top_comments.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Top Comments
                  </p>
                  <div className="space-y-2">
                    {post.reddit_data.top_comments.slice(0, 3).map((comment, i) => (
                      <div key={i} className="text-xs bg-white rounded p-2">
                        <p className="text-gray-600 font-medium">
                          u/{comment.author} · {comment.score} pts
                        </p>
                        <p className="text-gray-700 mt-1 line-clamp-2">
                          {comment.body}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            disabled={saving}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default PostEditor
