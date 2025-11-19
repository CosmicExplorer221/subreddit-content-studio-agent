import { useState } from 'react'
import { X, Download } from 'lucide-react'
import { useCategoryStore } from '@/store/useCategoryStore'
import * as api from '@/api/client'
import { useJobStore } from '@/store/useJobStore'

interface FetchDialogProps {
  open: boolean
  onClose: () => void
  onSuccess?: (jobId: string) => void
}

const FetchDialog = ({ open, onClose, onSuccess }: FetchDialogProps) => {
  const { categories } = useCategoryStore()
  const { addJob, pollJob, setActiveJob } = useJobStore()

  const [selectedCategory, setSelectedCategory] = useState('')
  const [timeFilter, setTimeFilter] = useState<'week' | 'day' | 'month'>('week')
  const [limit, setLimit] = useState(10)
  const [downloadMedia, setDownloadMedia] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFetch = async () => {
    if (!selectedCategory) {
      setError('Please select a category')
      return
    }

    setLoading(true)
    setError('')

    try {
      const { data: jobResponse } = await api.fetchRedditPosts(
        {
          category: selectedCategory,
          time_filter: timeFilter,
          limit,
        },
        downloadMedia
      )

      // Add job to store
      addJob({
        job_id: jobResponse.job_id,
        type: 'reddit_fetch',
        status: 'queued',
      })

      setActiveJob(jobResponse.job_id)

      // Start polling
      pollJob(jobResponse.job_id, undefined, 120)
        .then(() => {
          if (onSuccess) {
            onSuccess(jobResponse.job_id)
          }
          onClose()
        })
        .catch((err) => {
          setError(err.message)
        })
        .finally(() => {
          setLoading(false)
        })
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
      setLoading(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Fetch Reddit Posts
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
              {error}
            </div>
          )}

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category *
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">Select a category...</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
            {selectedCategory && (
              <p className="text-xs text-gray-500 mt-1">
                Subreddits:{' '}
                {categories
                  .find((c) => c.id === selectedCategory)
                  ?.subreddits.join(', ')}
              </p>
            )}
          </div>

          {/* Time Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time Period
            </label>
            <select
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="day">Past Day</option>
              <option value="week">Past Week</option>
              <option value="month">Past Month</option>
            </select>
          </div>

          {/* Limit */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Number of Posts
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value) || 10)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Download Media */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="downloadMedia"
              checked={downloadMedia}
              onChange={(e) => setDownloadMedia(e.target.checked)}
              className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
            />
            <label
              htmlFor="downloadMedia"
              className="text-sm text-gray-700 cursor-pointer"
            >
              Download images and videos
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={handleFetch}
            disabled={loading || !selectedCategory}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4" />
            {loading ? 'Fetching...' : 'Fetch Posts'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default FetchDialog
