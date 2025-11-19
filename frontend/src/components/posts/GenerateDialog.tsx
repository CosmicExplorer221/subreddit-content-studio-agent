import { useState } from 'react'
import { X, Sparkles } from 'lucide-react'
import { useTemplateStore } from '@/store/useTemplateStore'
import * as api from '@/api/client'
import { useJobStore } from '@/store/useJobStore'

interface GenerateDialogProps {
  open: boolean
  onClose: () => void
  postIds: string[]
  onSuccess?: (jobId: string) => void
}

const GenerateDialog = ({
  open,
  onClose,
  postIds,
  onSuccess,
}: GenerateDialogProps) => {
  const { templates } = useTemplateStore()
  const { addJob, pollJob, setActiveJob } = useJobStore()

  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [variations, setVariations] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    setLoading(true)
    setError('')

    try {
      const { data: jobResponse } = await api.generateContent({
        post_ids: postIds,
        template_id: selectedTemplate || undefined,
        variations,
      })

      // Add job to store
      addJob({
        job_id: jobResponse.job_id,
        type: 'content_generation',
        status: 'queued',
      })

      setActiveJob(jobResponse.job_id)

      // Start polling
      pollJob(jobResponse.job_id, undefined, 180)
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
            Generate LinkedIn Content
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
            Generating content for {postIds.length} post(s)
          </div>

          {/* Template */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Template
            </label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">Use category default</option>
              {templates.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name}
                </option>
              ))}
            </select>
            {selectedTemplate && (
              <p className="text-xs text-gray-500 mt-1">
                {templates.find((t) => t.id === selectedTemplate)?.description}
              </p>
            )}
          </div>

          {/* Variations */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Variations per post
            </label>
            <input
              type="number"
              min="1"
              max="3"
              value={variations}
              onChange={(e) => setVariations(parseInt(e.target.value) || 1)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              The best variation will be automatically selected
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
            onClick={handleGenerate}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Sparkles className="w-4 h-4" />
            {loading ? 'Generating...' : 'Generate Content'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default GenerateDialog
