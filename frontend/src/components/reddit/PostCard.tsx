import { formatDistanceToNow } from 'date-fns'
import { ArrowBigUp, MessageCircle, ExternalLink, Image, Video } from 'lucide-react'
import type { Post } from '@/types'

interface PostCardProps {
  post: Post
  selected?: boolean
  onSelect?: () => void
  onViewDetails?: () => void
}

const PostCard = ({ post, selected, onSelect, onViewDetails }: PostCardProps) => {
  const { reddit_data } = post

  const getMediaIcon = () => {
    if (!reddit_data.media_type) return null
    if (reddit_data.media_type === 'video') return <Video className="w-4 h-4" />
    if (reddit_data.media_type === 'image' || reddit_data.media_type === 'gallery') {
      return <Image className="w-4 h-4" />
    }
    return null
  }

  const createdDate = new Date(reddit_data.created_utc * 1000)

  return (
    <div
      className={`bg-white border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer ${
        selected ? 'border-primary-500 ring-2 ring-primary-200' : 'border-gray-200'
      }`}
      onClick={onViewDetails}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-gray-900 line-clamp-2 mb-1">
            {reddit_data.title}
          </h3>
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <span className="font-medium">r/{reddit_data.subreddit}</span>
            <span>•</span>
            <span>u/{reddit_data.author}</span>
            <span>•</span>
            <span>{formatDistanceToNow(createdDate, { addSuffix: true })}</span>
          </div>
        </div>

        {onSelect && (
          <input
            type="checkbox"
            checked={selected}
            onChange={(e) => {
              e.stopPropagation()
              onSelect()
            }}
            className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
          />
        )}
      </div>

      {/* Content Preview */}
      {reddit_data.content && (
        <p className="text-sm text-gray-600 line-clamp-2 mb-3">
          {reddit_data.content}
        </p>
      )}

      {/* Stats */}
      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-1.5 text-gray-700">
          <ArrowBigUp className="w-4 h-4" />
          <span className="font-medium">{reddit_data.score.toLocaleString()}</span>
          <span className="text-gray-500">
            ({Math.round(reddit_data.upvote_ratio * 100)}%)
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-gray-700">
          <MessageCircle className="w-4 h-4" />
          <span>{reddit_data.num_comments.toLocaleString()}</span>
        </div>

        {reddit_data.media_type && (
          <div className="flex items-center gap-1.5 text-primary-600">
            {getMediaIcon()}
            <span className="text-xs">
              {reddit_data.media_urls.length} file(s)
            </span>
          </div>
        )}

        {reddit_data.flair && (
          <span className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">
            {reddit_data.flair}
          </span>
        )}

        <a
          href={`https://reddit.com${reddit_data.permalink}`}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="ml-auto flex items-center gap-1 text-primary-600 hover:text-primary-700"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      {/* Status Badge */}
      {post.status && post.status !== 'draft' && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              post.status === 'published'
                ? 'bg-green-100 text-green-800'
                : post.status === 'review'
                ? 'bg-yellow-100 text-yellow-800'
                : post.status === 'approved'
                ? 'bg-blue-100 text-blue-800'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {post.status}
          </span>
        </div>
      )}
    </div>
  )
}

export default PostCard
