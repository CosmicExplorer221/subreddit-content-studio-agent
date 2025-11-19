import { useEffect, useState } from 'react'
import { FileText, TrendingUp, Clock, CheckCircle } from 'lucide-react'
import Header from '@/components/layout/Header'
import * as api from '@/api/client'
import { useCategoryStore } from '@/store/useCategoryStore'
import { useTemplateStore } from '@/store/useTemplateStore'

const Dashboard = () => {
  const { categories, fetchCategories } = useCategoryStore()
  const { templates, fetchTemplates } = useTemplateStore()
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCategories()
    fetchTemplates()

    api.getPostsStats().then(({ data }) => {
      setStats(data)
      setLoading(false)
    })
  }, [])

  if (loading) {
    return (
      <div>
        <Header title="Dashboard" subtitle="Overview of your content automation" />
        <div className="p-6">
          <div className="animate-pulse">Loading...</div>
        </div>
      </div>
    )
  }

  const statCards = [
    {
      title: 'Total Posts',
      value: stats?.total_posts || 0,
      icon: FileText,
      color: 'blue',
    },
    {
      title: 'In Review',
      value: stats?.by_status?.review || 0,
      icon: Clock,
      color: 'yellow',
    },
    {
      title: 'Approved',
      value: stats?.by_status?.approved || 0,
      icon: CheckCircle,
      color: 'green',
    },
    {
      title: 'Published',
      value: stats?.by_status?.published || 0,
      icon: TrendingUp,
      color: 'purple',
    },
  ]

  return (
    <div>
      <Header
        title="Dashboard"
        subtitle="Overview of your LinkedIn content automation"
      />

      <div className="p-6 space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat) => (
            <div
              key={stat.title}
              className="bg-white rounded-lg border border-gray-200 p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {stat.value}
                  </p>
                </div>
                <div
                  className={`p-3 rounded-lg bg-${stat.color}-100 text-${stat.color}-600`}
                >
                  <stat.icon className="w-6 h-6" />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Categories */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Categories
            </h2>
            <div className="space-y-3">
              {categories.map((category) => (
                <div
                  key={category.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">{category.name}</p>
                    <p className="text-sm text-gray-600">
                      {category.subreddits.length} subreddits
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-gray-900">
                      {stats?.by_category?.[category.id] || 0}
                    </p>
                    <p className="text-xs text-gray-600">posts</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Templates */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Templates
            </h2>
            <div className="space-y-3">
              {templates.map((template) => (
                <div
                  key={template.id}
                  className="p-3 bg-gray-50 rounded-lg"
                >
                  <p className="font-medium text-gray-900">{template.name}</p>
                  <p className="text-sm text-gray-600 mt-1">
                    {template.description}
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                    <span>
                      Length: {template.target_length.min}-
                      {template.target_length.max}
                    </span>
                    <span>
                      Tags: {template.hashtag_count.min}-
                      {template.hashtag_count.max}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/reddit"
              className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
            >
              <p className="font-medium text-gray-900">Fetch Reddit Posts</p>
              <p className="text-sm text-gray-600 mt-1">
                Browse and import content
              </p>
            </a>
            <a
              href="/posts"
              className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
            >
              <p className="font-medium text-gray-900">Generate Content</p>
              <p className="text-sm text-gray-600 mt-1">
                Create LinkedIn posts
              </p>
            </a>
            <a
              href="/notion"
              className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
            >
              <p className="font-medium text-gray-900">Sync to Notion</p>
              <p className="text-sm text-gray-600 mt-1">
                Manage in your database
              </p>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
