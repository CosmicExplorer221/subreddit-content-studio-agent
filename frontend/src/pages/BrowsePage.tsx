// Browse Posts Page
import { useEffect, useState } from 'react'
import { Sparkles, Loader2 } from 'lucide-react'
import { useStore } from '../store/useStore'
import { PostCard } from '../components/PostCard'

export function BrowsePage() {
  const {
    posts,
    templates,
    selectedPostIds,
    loading,
    error,
    loadPosts,
    loadTemplates,
    togglePostSelection,
    generateContent
  } = useStore()

  const [selectedTemplate, setSelectedTemplate] = useState('railway_professional')

  useEffect(() => {
    loadPosts()
    loadTemplates()
  }, [])

  const handleGenerate = () => {
    if (selectedPostIds.size > 0) {
      generateContent(selectedTemplate)
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Browse Railway Posts</h1>
        <p className="text-gray-600">
          Select posts to generate LinkedIn content with AI
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Action Bar */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Template:</label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-railway-500"
            >
              {templates.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleGenerate}
            disabled={selectedPostIds.size === 0 || loading}
            className="btn btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Content ({selectedPostIds.size})
              </>
            )}
          </button>

          <div className="ml-auto text-sm text-gray-600">
            {selectedPostIds.size} of {posts.length} selected
          </div>
        </div>
      </div>

      {/* Posts Grid */}
      {loading && posts.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-railway-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              selected={selectedPostIds.has(post.id)}
              onToggle={() => togglePostSelection(post.id)}
            />
          ))}
        </div>
      )}

      {posts.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500">
          <p>No posts available</p>
        </div>
      )}
    </div>
  )
}
