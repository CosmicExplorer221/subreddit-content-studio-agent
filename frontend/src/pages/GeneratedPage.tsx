// Generated Content Page
import { useEffect } from 'react'
import { Send, Sparkles, Loader2 } from 'lucide-react'
import { useStore } from '../store/useStore'
import { GeneratedPostCard } from '../components/GeneratedPostCard'

export function GeneratedPage() {
  const {
    generatedPosts,
    selectedGenPostIds,
    loading,
    error,
    loadGeneratedPosts,
    toggleGenPostSelection,
    syncToNotion,
    deleteGeneratedPost
  } = useStore()

  useEffect(() => {
    loadGeneratedPosts()
  }, [])

  const handleSync = () => {
    if (selectedGenPostIds.size > 0) {
      syncToNotion()
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Generated Content</h1>
        <p className="text-gray-600">
          Review and manage your AI-generated LinkedIn posts
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Action Bar */}
      {generatedPosts.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-wrap gap-4 items-center">
            <button
              onClick={handleSync}
              disabled={selectedGenPostIds.size === 0 || loading}
              className="btn btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Syncing...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Sync to Notion ({selectedGenPostIds.size})
                </>
              )}
            </button>

            <div className="ml-auto text-sm text-gray-600">
              {selectedGenPostIds.size} of {generatedPosts.length} selected
            </div>
          </div>
        </div>
      )}

      {/* Generated Posts */}
      {loading && generatedPosts.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-railway-600" />
        </div>
      ) : generatedPosts.length > 0 ? (
        <div className="space-y-4">
          {generatedPosts.map((post) => (
            <GeneratedPostCard
              key={post.id}
              post={post}
              selected={selectedGenPostIds.has(post.id)}
              onToggle={() => toggleGenPostSelection(post.id)}
              onDelete={() => deleteGeneratedPost(post.id)}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <Sparkles className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Generated Content Yet
          </h3>
          <p className="text-gray-600 mb-4">
            Select posts from the Browse page and click "Generate Content" to get started.
          </p>
        </div>
      )}
    </div>
  )
}
