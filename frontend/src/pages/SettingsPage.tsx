// Settings Page with API Key Configuration
import { useEffect, useState } from 'react'
import { Save, Key, Database, CheckCircle, XCircle, Loader2, Eye, EyeOff } from 'lucide-react'
import { getAPIKeysStatus, updateSettings } from '../api/client'
import type { APIKeysStatus } from '../types'

export function SettingsPage() {
  const [apiKeysStatus, setApiKeysStatus] = useState<APIKeysStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  // Form state
  const [geminiKey, setGeminiKey] = useState('')
  const [notionKey, setNotionKey] = useState('')
  const [notionDbId, setNotionDbId] = useState('')

  // Show/hide passwords
  const [showGemini, setShowGemini] = useState(false)
  const [showNotion, setShowNotion] = useState(false)
  const [showDbId, setShowDbId] = useState(false)

  useEffect(() => {
    loadStatus()
  }, [])

  const loadStatus = async () => {
    setLoading(true)
    try {
      const status = await getAPIKeysStatus()
      setApiKeysStatus(status)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)

    try {
      const updates: any = {}
      if (geminiKey) updates.gemini_api_key = geminiKey
      if (notionKey) updates.notion_api_key = notionKey
      if (notionDbId) updates.notion_database_id = notionDbId

      if (Object.keys(updates).length === 0) {
        setMessage({ type: 'error', text: 'No changes to save' })
        setSaving(false)
        return
      }

      await updateSettings(updates)
      setMessage({ type: 'success', text: 'Settings saved successfully! (Current session only)' })

      // Clear form
      setGeminiKey('')
      setNotionKey('')
      setNotionDbId('')

      // Reload status
      await loadStatus()
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to save settings' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-8 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600">
          Configure API keys and application settings
        </p>
      </div>

      {/* Message */}
      {message && (
        <div
          className={`px-4 py-3 rounded-lg mb-6 ${
            message.type === 'success'
              ? 'bg-green-50 border border-green-200 text-green-800'
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* API Keys Status */}
      <div className="card mb-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Key className="w-5 h-5" />
          API Keys Status
        </h2>

        {loading ? (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="w-6 h-6 animate-spin text-railway-600" />
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="font-medium">Gemini API</span>
              </div>
              <div className="flex items-center gap-2">
                {apiKeysStatus?.gemini_configured ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-green-600 font-medium">Configured</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5 text-red-600" />
                    <span className="text-sm text-red-600 font-medium">Not Configured</span>
                  </>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="font-medium">Notion API</span>
              </div>
              <div className="flex items-center gap-2">
                {apiKeysStatus?.notion_configured ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-green-600 font-medium">Configured</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5 text-red-600" />
                    <span className="text-sm text-red-600 font-medium">Not Configured</span>
                  </>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="font-medium">Notion Database</span>
              </div>
              <div className="flex items-center gap-2">
                {apiKeysStatus?.notion_database_configured ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-green-600 font-medium">Configured</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5 text-red-600" />
                    <span className="text-sm text-red-600 font-medium">Not Configured</span>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* API Keys Form */}
      <div className="card">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Database className="w-5 h-5" />
          Configure API Keys
        </h2>

        <div className="space-y-4">
          {/* Gemini API Key */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gemini API Key
            </label>
            <div className="relative">
              <input
                type={showGemini ? 'text' : 'password'}
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                placeholder="Enter your Gemini API key"
                className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-railway-500 focus:border-transparent"
              />
              <button
                type="button"
                onClick={() => setShowGemini(!showGemini)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showGemini ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Get your key from:{' '}
              <a
                href="https://makersuite.google.com/app/apikey"
                target="_blank"
                rel="noopener noreferrer"
                className="text-railway-600 hover:underline"
              >
                https://makersuite.google.com/app/apikey
              </a>
            </p>
          </div>

          {/* Notion API Key */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notion API Key
            </label>
            <div className="relative">
              <input
                type={showNotion ? 'text' : 'password'}
                value={notionKey}
                onChange={(e) => setNotionKey(e.target.value)}
                placeholder="Enter your Notion API key"
                className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-railway-500 focus:border-transparent"
              />
              <button
                type="button"
                onClick={() => setShowNotion(!showNotion)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showNotion ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Get your key from:{' '}
              <a
                href="https://www.notion.so/my-integrations"
                target="_blank"
                rel="noopener noreferrer"
                className="text-railway-600 hover:underline"
              >
                https://www.notion.so/my-integrations
              </a>
            </p>
          </div>

          {/* Notion Database ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notion Database ID
            </label>
            <div className="relative">
              <input
                type={showDbId ? 'text' : 'password'}
                value={notionDbId}
                onChange={(e) => setNotionDbId(e.target.value)}
                placeholder="Enter your Notion database ID"
                className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-railway-500 focus:border-transparent"
              />
              <button
                type="button"
                onClick={() => setShowDbId(!showDbId)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showDbId ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Find this in your Notion database URL (the 32-character string)
            </p>
          </div>

          {/* Warning */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">
              <strong>Note:</strong> These settings are for the current session only.
              For permanent configuration, edit the <code className="bg-yellow-100 px-1 rounded">backend/.env</code> file.
            </p>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={saving || (!geminiKey && !notionKey && !notionDbId)}
            className="btn btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Settings
              </>
            )}
          </button>
        </div>
      </div>

      {/* Help Section */}
      <div className="card mt-6 bg-blue-50 border border-blue-200">
        <h3 className="font-bold text-blue-900 mb-2">Need Help?</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• API keys are required for AI generation and Notion sync</li>
          <li>• You can test the app without API keys using the Browse page</li>
          <li>• For production use, configure keys in backend/.env file</li>
          <li>• Check the README.md for detailed setup instructions</li>
        </ul>
      </div>
    </div>
  )
}
