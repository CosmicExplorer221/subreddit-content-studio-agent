import { useState } from 'react'
import { X, Database } from 'lucide-react'
import * as api from '@/api/client'
import { useJobStore } from '@/store/useJobStore'

interface SyncDialogProps {
  open: boolean
  onClose: () => void
  postIds: string[]
  onSuccess?: (jobId: string) => void
}

const SyncDialog = ({ open, onClose, postIds, onSuccess }: SyncDialogProps) => {
  const { addJob, pollJob, setActiveJob } = useJobStore()

  const [updateExisting, setUpdateExisting] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSync = async () => {
    setLoading(true)
    setError('')

    try {
      const { data: jobResponse } = await api.syncToNotion({
        post_ids: postIds,
        update_existing: updateExisting,
      })

      // Add job to store
      addJob({
        job_id: jobResponse.job_id,
        type: 'notion_sync',
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
            Sync to Notion
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

          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
            Syncing {postIds.length} post(s) to your Notion database
          </div>

          {/* Update Existing */}
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="updateExisting"
              checked={updateExisting}
              onChange={(e) => setUpdateExisting(e.target.checked)}
              className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500 mt-1"
            />
            <div className="flex-1">
              <label
                htmlFor="updateExisting"
                className="text-sm font-medium text-gray-700 cursor-pointer"
              >
                Update existing pages
              </label>
              <p className="text-xs text-gray-500 mt-0.5">
                If enabled, existing Notion pages will be updated. Otherwise,
                duplicate posts will be skipped.
              </p>
            </div>
          </div>

          <div className="p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-600">
              <strong>Note:</strong> Duplicate detection is based on Reddit post
              ID. Posts with the same Reddit ID will not create duplicate Notion
              pages.
            </p>
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
            onClick={handleSync}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Database className="w-4 h-4" />
            {loading ? 'Syncing...' : 'Sync to Notion'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default SyncDialog
