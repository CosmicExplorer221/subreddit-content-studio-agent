// Post Card Component - Reusable
import type { Post } from '../types'

interface PostCardProps {
  post: Post
  selected: boolean
  onToggle: () => void
}

export function PostCard({ post, selected, onToggle }: PostCardProps) {
  return (
    <div
      className={`card cursor-pointer transition ${
        selected ? 'ring-2 ring-railway-600' : ''
      }`}
      onClick={onToggle}
    >
      <div className="flex items-start gap-3 mb-3">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggle}
          onClick={(e) => e.stopPropagation()}
          className="mt-1 w-5 h-5 cursor-pointer"
        />
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-2">{post.title}</h3>
          <p className="text-sm text-gray-600 line-clamp-3">{post.content}</p>
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm text-gray-500 mt-4 pt-4 border-t">
        <span className="flex items-center gap-1">
          ⬆️ {post.score.toLocaleString()}
        </span>
        <span className="flex items-center gap-1">
          💬 {post.num_comments}
        </span>
        {post.has_media && <span>📷</span>}
        <span className="text-xs text-gray-400 ml-auto">
          {post.author}
        </span>
      </div>
    </div>
  )
}
