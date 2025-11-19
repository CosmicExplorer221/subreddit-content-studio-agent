import { useEffect } from 'react'
import { Key, Database, Sparkles, Settings as SettingsIcon } from 'lucide-react'
import Header from '@/components/layout/Header'
import * as api from '@/api/client'
import { useCategoryStore } from '@/store/useCategoryStore'
import { useTemplateStore } from '@/store/useTemplateStore'

const SettingsPage = () => {
  const { categories, fetchCategories } = useCategoryStore()
  const { templates, fetchTemplates } = useTemplateStore()

  useEffect(() => {
    fetchCategories()
    fetchTemplates()
  }, [])

  return (
    <div>
      <Header
        title="Settings"
        subtitle="Configure your LinkedIn automation tool"
      />

      <div className="p-6 space-y-6">
        {/* API Configuration */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <Key className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">
                API Configuration
              </h2>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Configure your API keys and credentials
            </p>
          </div>

          <div className="p-6 space-y-6">
            {/* Reddit */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Reddit API</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-700 mb-3">
                  API keys are configured in the backend <code className="bg-gray-200 px-1 py-0.5 rounded">.env</code> file.
                </p>
                <p className="text-xs text-gray-600">
                  Location: <code>backend/.env</code>
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  Required: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
                </p>
              </div>
            </div>

            {/* Gemini */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Gemini API
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-700 mb-3">
                  Configure in backend <code className="bg-gray-200 px-1 py-0.5 rounded">.env</code> file.
                </p>
                <p className="text-xs text-gray-600">
                  Required: GEMINI_API_KEY
                </p>
                <a
                  href="https://makersuite.google.com/app/apikey"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary-600 hover:text-primary-700 mt-2 inline-block"
                >
                  Get API Key →
                </a>
              </div>
            </div>

            {/* Notion */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Database className="w-4 h-4" />
                Notion API
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-700 mb-3">
                  Configure in backend <code className="bg-gray-200 px-1 py-0.5 rounded">.env</code> file.
                </p>
                <p className="text-xs text-gray-600">
                  Required: NOTION_API_TOKEN, NOTION_DATABASE_ID
                </p>
                <a
                  href="https://www.notion.so/my-integrations"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary-600 hover:text-primary-700 mt-2 inline-block"
                >
                  Get API Token →
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Categories */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <SettingsIcon className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">Categories</h2>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {categories.length} content categories configured
            </p>
          </div>

          <div className="p-6">
            <div className="space-y-4">
              {categories.map((category) => (
                <div
                  key={category.id}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <h3 className="font-medium text-gray-900">{category.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {category.description}
                  </p>
                  <div className="mt-3 space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">Subreddits:</span>
                      <span className="ml-2 text-gray-900">
                        {category.subreddits.join(', ')}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Hashtags:</span>
                      <span className="ml-2 text-gray-900">
                        {category.hashtags.join(' ')}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Templates */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">Templates</h2>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {templates.length} content templates configured
            </p>
          </div>

          <div className="p-6">
            <div className="space-y-4">
              {templates.map((template) => (
                <div
                  key={template.id}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <h3 className="font-medium text-gray-900">{template.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {template.description}
                  </p>
                  <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Length:</span>
                      <span className="ml-2 text-gray-900">
                        {template.target_length.min}-{template.target_length.max} chars
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Hashtags:</span>
                      <span className="ml-2 text-gray-900">
                        {template.hashtag_count.min}-{template.hashtag_count.max} tags
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Tone:</span>
                      <span className="ml-2 text-gray-900">
                        {template.style.tone}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Emoji:</span>
                      <span className="ml-2 text-gray-900">
                        {template.style.emoji_usage}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SettingsPage
