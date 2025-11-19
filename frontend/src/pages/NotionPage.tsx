// Notion Sync Page
import { useEffect } from 'react'
import { Send, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { useStore } from '../store/useStore'

export function NotionPage() {
  const {
    generatedPosts,
    loading,
    error,
    loadGeneratedPosts
  } = useStore()

  useEffect(() => {
    loadGeneratedPosts()
  }, [])

  const syncedPosts = generatedPosts.filter((p) => p.notion_page_id)
  const unsyncedPosts = generatedPosts.filter((p) => !p.notion_page_id)

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Notion Sync Status</h1>
        <p className="text-gray-600">
          View sync status of your generated content
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-railway-100 rounded-lg">
              <Send className="w-6 h-6 text-railway-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Generated</p>
              <p className="text-2xl font-bold text-gray-900">
                {generatedPosts.length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Synced to Notion</p>
              <p className="text-2xl font-bold text-gray-900">
                {syncedPosts.length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <XCircle className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Not Synced</p>
              <p className="text-2xl font-bold text-gray-900">
                {unsyncedPosts.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Synced Posts */}
      {syncedPosts.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Synced to Notion ({syncedPosts.length})
          </h2>
          <div className="space-y-3">
            {syncedPosts.map((post) => (
              <div key={post.id} className="card">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {post.source_post.title}
                    </h3>
                    <p className="text-sm text-gray-600">
                      Synced: {new Date(post.notion_synced_at!).toLocaleString()}
                    </p>
                  </div>
                  <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                    ✓ Synced
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Unsynced Posts */}
      {unsyncedPosts.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Not Synced Yet ({unsyncedPosts.length})
          </h2>
          <div className="space-y-3">
            {unsyncedPosts.map((post) => (
              <div key={post.id} className="card">
                <div className="flex items-start gap-3">
                  <XCircle className="w-5 h-5 text-yellow-600 mt-1" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {post.source_post.title}
                    </h3>
                    <p className="text-sm text-gray-600">
                      Status: {post.status}
                    </p>
                  </div>
                  <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full">
                    Not Synced
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-800">
              💡 Go to <strong>Generated Content</strong> page to select and sync these posts to Notion
            </p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-railway-600" />
        </div>
      )}

      {/* Empty State */}
      {!loading && generatedPosts.length === 0 && (
        <div className="text-center py-16">
          <Send className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Content Generated Yet
          </h3>
          <p className="text-gray-600">
            Generate some content first to see sync status here
          </p>
        </div>
      )}
    </div>
  )
}
