// Generated Post Card Component - Reusable
import { Trash2 } from 'lucide-react'
import type { GeneratedPost } from '../types'

interface GeneratedPostCardProps {
  post: GeneratedPost
  selected: boolean
  onToggle: () => void
  onDelete: () => void
}

export function GeneratedPostCard({
  post,
  selected,
  onToggle,
  onDelete
}: GeneratedPostCardProps) {
  return (
    <div
      className={`card transition ${selected ? 'ring-2 ring-railway-600' : ''}`}
    >
      <div className="flex items-start gap-3 mb-4">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggle}
          className="mt-1 w-5 h-5 cursor-pointer"
        />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold text-gray-900 flex-1">
              {post.source_post.title}
            </h3>
            <span
              className={`px-2 py-1 text-xs rounded-full ${
                post.notion_page_id
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {post.notion_page_id ? '✓ Synced' : post.status}
            </span>
          </div>

          <div className="bg-gray-50 rounded-lg p-4 mb-3">
            <p className="text-sm text-gray-700 whitespace-pre-wrap">
              {post.generated_content.content.slice(0, 500)}
              {post.generated_content.content.length > 500 && '...'}
            </p>
          </div>

          <div className="flex items-center gap-4 text-sm flex-wrap">
            <span className="text-gray-600">
              Quality: {post.generated_content.quality_score}/100
            </span>
            <span className="text-gray-600">
              Template: {post.generated_content.template_id.replace('railway_', '')}
            </span>
            <div className="flex gap-1">
              {post.generated_content.hashtags.slice(0, 3).map((tag) => (
                <span key={tag} className="text-xs bg-railway-100 text-railway-800 px-2 py-1 rounded">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete()
          }}
          className="p-2 text-gray-400 hover:text-red-600 transition"
          title="Delete"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
