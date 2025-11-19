import { useEffect, useState } from 'react'
import { Train, Sparkles, Send, Trash2 } from 'lucide-react'
import { useStore } from './store/useStore'
import type { Post, GeneratedPost } from './types'

function App() {
  const {
    posts,
    generatedPosts,
    templates,
    selectedPostIds,
    selectedGenPostIds,
    loading,
    error,
    loadPosts,
    loadGeneratedPosts,
    loadTemplates,
    togglePostSelection,
    toggleGenPostSelection,
    generateContent,
    syncToNotion,
    deleteGeneratedPost
  } = useStore()

  const [activeTab, setActiveTab] = useState<'browse' | 'generated'>('browse')
  const [selectedTemplate, setSelectedTemplate] = useState('railway_professional')

  useEffect(() => {
    loadPosts()
    loadGeneratedPosts()
    loadTemplates()
  }, [])

  const handleGenerate = () => {
    if (selectedPostIds.size > 0) {
      generateContent(selectedTemplate)
    }
  }

  const handleSync = () => {
    if (selectedGenPostIds.size > 0) {
      syncToNotion()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-railway-800 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <Train className="w-8 h-8" />
            <div>
              <h1 className="text-2xl font-bold">LinkedIn Content Studio</h1>
              <p className="text-railway-200 text-sm">Railway Edition - AI-Powered Content Generation</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('browse')}
            className={`px-6 py-3 rounded-lg font-medium transition ${
              activeTab === 'browse'
                ? 'bg-railway-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Browse Posts ({posts.length})
          </button>
          <button
            onClick={() => setActiveTab('generated')}
            className={`px-6 py-3 rounded-lg font-medium transition ${
              activeTab === 'generated'
                ? 'bg-railway-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Generated Content ({generatedPosts.length})
          </button>
        </div>

        {/* Browse Tab */}
        {activeTab === 'browse' && (
          <div>
            {/* Actions */}
            <div className="bg-white rounded-lg shadow-md p-4 mb-6 flex gap-4 items-center">
              <select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg"
              >
                {templates.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>

              <button
                onClick={handleGenerate}
                disabled={selectedPostIds.size === 0 || loading}
                className="btn btn-primary flex items-center gap-2 disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                Generate Content ({selectedPostIds.size})
              </button>

              <div className="ml-auto text-sm text-gray-600">
                {selectedPostIds.size} selected
              </div>
            </div>

            {/* Posts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {posts.map(post => (
                <PostCard
                  key={post.id}
                  post={post}
                  selected={selectedPostIds.has(post.id)}
                  onToggle={() => togglePostSelection(post.id)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Generated Tab */}
        {activeTab === 'generated' && (
          <div>
            {/* Actions */}
            <div className="bg-white rounded-lg shadow-md p-4 mb-6 flex gap-4 items-center">
              <button
                onClick={handleSync}
                disabled={selectedGenPostIds.size === 0 || loading}
                className="btn btn-primary flex items-center gap-2 disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                Sync to Notion ({selectedGenPostIds.size})
              </button>

              <div className="ml-auto text-sm text-gray-600">
                {selectedGenPostIds.size} selected
              </div>
            </div>

            {/* Generated Posts Grid */}
            <div className="grid grid-cols-1 gap-6">
              {generatedPosts.map(post => (
                <GeneratedPostCard
                  key={post.id}
                  post={post}
                  selected={selectedGenPostIds.has(post.id)}
                  onToggle={() => toggleGenPostSelection(post.id)}
                  onDelete={() => deleteGeneratedPost(post.id)}
                />
              ))}
            </div>

            {generatedPosts.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No generated content yet.</p>
                <p className="text-sm">Select posts and click "Generate Content" to get started.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// Post Card Component
function PostCard({ post, selected, onToggle }: { post: Post; selected: boolean; onToggle: () => void }) {
  return (
    <div className={`card cursor-pointer transition ${selected ? 'ring-2 ring-railway-600' : ''}`}>
      <div className="flex items-start gap-3 mb-3">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggle}
          className="mt-1 w-5 h-5"
        />
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-2">{post.title}</h3>
          <p className="text-sm text-gray-600 line-clamp-3">{post.content}</p>
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm text-gray-500 mt-4 pt-4 border-t">
        <span>⬆️ {post.score}</span>
        <span>💬 {post.num_comments}</span>
        {post.has_media && <span>📷</span>}
      </div>
    </div>
  )
}

// Generated Post Card Component
function GeneratedPostCard({
  post,
  selected,
  onToggle,
  onDelete
}: {
  post: GeneratedPost;
  selected: boolean;
  onToggle: () => void;
  onDelete: () => void;
}) {
  return (
    <div className={`card transition ${selected ? 'ring-2 ring-railway-600' : ''}`}>
      <div className="flex items-start gap-3 mb-4">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggle}
          className="mt-1 w-5 h-5"
        />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold text-gray-900">{post.source_post.title}</h3>
            <span className={`px-2 py-1 text-xs rounded-full ${
              post.notion_page_id
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {post.notion_page_id ? 'Synced' : post.status}
            </span>
          </div>

          <div className="bg-gray-50 rounded-lg p-4 mb-3">
            <p className="text-sm text-gray-700 whitespace-pre-wrap">
              {post.generated_content.content.slice(0, 500)}
              {post.generated_content.content.length > 500 && '...'}
            </p>
          </div>

          <div className="flex items-center gap-3 text-sm">
            <span className="text-gray-600">Quality: {post.generated_content.quality_score}/100</span>
            <span className="text-gray-600">
              {post.generated_content.hashtags.slice(0, 3).join(' ')}
            </span>
          </div>
        </div>

        <button
          onClick={onDelete}
          className="p-2 text-gray-400 hover:text-red-600 transition"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

export default App
