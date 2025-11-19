import { useEffect, useState } from 'react'
import { Sparkles, Trash2, Edit } from 'lucide-react'
import Header from '@/components/layout/Header'
import PostCard from '@/components/reddit/PostCard'
import PostEditor from '@/components/posts/PostEditor'
import GenerateDialog from '@/components/posts/GenerateDialog'
import { usePostStore } from '@/store/usePostStore'
import { useCategoryStore } from '@/store/useCategoryStore'
import { useTemplateStore } from '@/store/useTemplateStore'
import type { Post, PostStatus } from '@/types'

const PostsPage = () => {
  const {
    posts,
    selectedPosts,
    fetchPosts,
    loading,
    filters,
    setFilters,
    toggleSelectPost,
    clearSelection,
    deletePost,
  } = usePostStore()
  const { categories, fetchCategories } = useCategoryStore()
  const { fetchTemplates } = useTemplateStore()

  const [generateDialogOpen, setGenerateDialogOpen] = useState(false)
  const [editingPost, setEditingPost] = useState<Post | null>(null)

  useEffect(() => {
    fetchCategories()
    fetchTemplates()
    fetchPosts()
  }, [])

  const selectedPostIds = Array.from(selectedPosts)
  const hasSelection = selectedPostIds.length > 0

  const handleGenerateSuccess = () => {
    fetchPosts()
    clearSelection()
  }

  const handleDeleteSelected = async () => {
    if (!window.confirm(`Delete ${selectedPostIds.length} post(s)?`)) return

    for (const id of selectedPostIds) {
      await deletePost(id)
    }
    clearSelection()
  }

  return (
    <div>
      <Header
        title="Posts"
        subtitle="Manage and generate LinkedIn content"
        actions={
          hasSelection && (
            <>
              <button
                onClick={() => setGenerateDialogOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700"
              >
                <Sparkles className="w-4 h-4" />
                Generate ({selectedPostIds.length})
              </button>
              <button
                onClick={handleDeleteSelected}
                className="flex items-center gap-2 px-4 py-2 border border-red-300 text-red-600 text-sm font-medium rounded-lg hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </>
          )
        }
      />

      <div className="p-6">
        {/* Filters */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={filters.category || ''}
                onChange={(e) =>
                  setFilters({ category: e.target.value || undefined })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filters.status || ''}
                onChange={(e) =>
                  setFilters({
                    status: (e.target.value as PostStatus) || undefined,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="review">In Review</option>
                <option value="approved">Approved</option>
                <option value="scheduled">Scheduled</option>
                <option value="published">Published</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <input
                type="text"
                value={filters.search || ''}
                onChange={(e) => setFilters({ search: e.target.value || undefined })}
                placeholder="Search posts..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Results Info */}
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

        {/* Posts Grid */}
        {loading && posts.length === 0 ? (
          <div className="text-center py-12">
            <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
            <p className="text-gray-600 mt-4">Loading posts...</p>
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No posts found</p>
            <a href="/reddit" className="mt-4 text-primary-600 hover:text-primary-700">
              Fetch posts from Reddit
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {posts.map((post) => (
              <div key={post.id} className="relative">
                <PostCard
                  post={post}
                  selected={selectedPosts.has(post.id)}
                  onSelect={() => toggleSelectPost(post.id)}
                  onViewDetails={() => setEditingPost(post)}
                />
                <button
                  onClick={() => setEditingPost(post)}
                  className="absolute top-2 right-2 p-2 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
                >
                  <Edit className="w-4 h-4 text-gray-600" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <GenerateDialog
        open={generateDialogOpen}
        onClose={() => setGenerateDialogOpen(false)}
        postIds={selectedPostIds}
        onSuccess={handleGenerateSuccess}
      />

      {editingPost && (
        <PostEditor
          post={editingPost}
          open={true}
          onClose={() => {
            setEditingPost(null)
            fetchPosts()
          }}
        />
      )}
    </div>
  )
}

export default PostsPage
