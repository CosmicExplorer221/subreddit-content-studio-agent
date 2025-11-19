import { useEffect, useState } from 'react'
import { Download, RefreshCw } from 'lucide-react'
import Header from '@/components/layout/Header'
import PostCard from '@/components/reddit/PostCard'
import FetchDialog from '@/components/reddit/FetchDialog'
import { usePostStore } from '@/store/usePostStore'
import { useCategoryStore } from '@/store/useCategoryStore'

const RedditPage = () => {
  const { posts, fetchPosts, loading, filters, setFilters } = usePostStore()
  const { categories, fetchCategories } = useCategoryStore()
  const [fetchDialogOpen, setFetchDialogOpen] = useState(false)

  useEffect(() => {
    fetchCategories()
    fetchPosts()
  }, [])

  const handleFetchSuccess = () => {
    fetchPosts()
  }

  return (
    <div>
      <Header
        title="Reddit Browser"
        subtitle="Fetch and browse Reddit posts"
        actions={
          <button
            onClick={() => setFetchDialogOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700"
          >
            <Download className="w-4 h-4" />
            Fetch Posts
          </button>
        }
      />

      <div className="p-6">
        {/* Filters */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <select
                value={filters.category || ''}
                onChange={(e) => setFilters({ category: e.target.value || undefined })}
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

            <button
              onClick={() => fetchPosts()}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Posts Grid */}
        {loading && posts.length === 0 ? (
          <div className="text-center py-12">
            <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
            <p className="text-gray-600 mt-4">Loading posts...</p>
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No posts found</p>
            <button
              onClick={() => setFetchDialogOpen(true)}
              className="mt-4 text-primary-600 hover:text-primary-700"
            >
              Fetch posts from Reddit
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        )}
      </div>

      <FetchDialog
        open={fetchDialogOpen}
        onClose={() => setFetchDialogOpen(false)}
        onSuccess={handleFetchSuccess}
      />
    </div>
  )
}

export default RedditPage
