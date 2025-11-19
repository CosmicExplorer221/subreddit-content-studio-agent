import { useEffect, useState } from 'react'
import { Database } from 'lucide-react'
import Header from '@/components/layout/Header'
import PostCard from '@/components/reddit/PostCard'
import SyncDialog from '@/components/notion/SyncDialog'
import { usePostStore } from '@/store/usePostStore'
import * as api from '@/api/client'

const NotionPage = () => {
  const {
    posts,
    selectedPosts,
    fetchPosts,
    loading,
    toggleSelectPost,
    clearSelection,
  } = usePostStore()

  const [syncDialogOpen, setSyncDialogOpen] = useState(false)
  const [notionStatus, setNotionStatus] = useState<any>(null)

  useEffect(() => {
    fetchPosts()
    api.getNotionStatus().then(({ data }) => setNotionStatus(data))
  }, [])

  const selectedPostIds = Array.from(selectedPosts)
  const hasSelection = selectedPostIds.length > 0

  // Filter posts that have LinkedIn content
  const readyPosts = posts.filter((p) => p.linkedin_content?.content)

  const handleSyncSuccess = () => {
    fetchPosts()
    clearSelection()
  }

  return (
    <div>
      <Header
        title="Notion Sync"
        subtitle="Sync your posts to Notion database"
        actions={
          hasSelection && (
            <button
              onClick={() => setSyncDialogOpen(true)}
              disabled={!notionStatus || notionStatus.status !== 'connected'}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Database className="w-4 h-4" />
              Sync ({selectedPostIds.length})
            </button>
          )
        }
      />

      <div className="p-6">
        {/* Notion Status */}
        <div
          className={`rounded-lg border p-4 mb-6 ${
            notionStatus?.status === 'connected'
              ? 'bg-green-50 border-green-200'
              : notionStatus?.status === 'not_configured'
              ? 'bg-yellow-50 border-yellow-200'
              : 'bg-red-50 border-red-200'
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p
                className={`font-medium ${
                  notionStatus?.status === 'connected'
                    ? 'text-green-900'
                    : notionStatus?.status === 'not_configured'
                    ? 'text-yellow-900'
                    : 'text-red-900'
                }`}
              >
                {notionStatus?.status === 'connected'
                  ? 'Connected to Notion'
                  : notionStatus?.status === 'not_configured'
                  ? 'Notion Not Configured'
                  : 'Connection Error'}
              </p>
              <p
                className={`text-sm mt-1 ${
                  notionStatus?.status === 'connected'
                    ? 'text-green-700'
                    : notionStatus?.status === 'not_configured'
                    ? 'text-yellow-700'
                    : 'text-red-700'
                }`}
              >
                {notionStatus?.message || 'Checking connection...'}
              </p>
              {notionStatus?.title && (
                <p className="text-sm text-gray-600 mt-1">
                  Database: {notionStatus.title}
                </p>
              )}
            </div>
            {notionStatus?.status === 'not_configured' && (
              <a
                href="/settings"
                className="px-4 py-2 bg-yellow-600 text-white text-sm font-medium rounded-lg hover:bg-yellow-700"
              >
                Configure
              </a>
            )}
          </div>
        </div>

        {/* Selection Info */}
        {hasSelection && (
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-primary-800">
              {selectedPostIds.length} post(s) selected
              <button
                onClick={clearSelection}
                className="ml-4 text-primary-600 hover:text-primary-700 underline"
              >
                Clear selection
              </button>
            </p>
          </div>
        )}

        {/* Posts Ready for Sync */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            Ready for Sync
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            {readyPosts.length} post(s) with generated LinkedIn content
          </p>

          {loading && posts.length === 0 ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
              <p className="text-gray-600 mt-4">Loading posts...</p>
            </div>
          ) : readyPosts.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600">No posts ready for sync</p>
              <p className="text-sm text-gray-500 mt-2">
                Generate LinkedIn content for your posts first
              </p>
              <a
                href="/posts"
                className="mt-4 inline-block text-primary-600 hover:text-primary-700"
              >
                Go to Posts
              </a>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
              {readyPosts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  selected={selectedPosts.has(post.id)}
                  onSelect={() => toggleSelectPost(post.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      <SyncDialog
        open={syncDialogOpen}
        onClose={() => setSyncDialogOpen(false)}
        postIds={selectedPostIds}
        onSuccess={handleSyncSuccess}
      />
    </div>
  )
}

export default NotionPage
