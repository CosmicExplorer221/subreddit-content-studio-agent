import { Bell, Search } from 'lucide-react'
import { useJobStore } from '@/store/useJobStore'

interface HeaderProps {
  title: string
  subtitle?: string
  actions?: React.ReactNode
}

const Header = ({ title, subtitle, actions }: HeaderProps) => {
  const { jobs, activeJobId } = useJobStore()

  const activeJob = activeJobId ? jobs.get(activeJobId) : null
  const hasActiveJobs = Array.from(jobs.values()).some(
    (job) => job.status === 'processing' || job.status === 'queued'
  )

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
        </div>

        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Notifications */}
          <button className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell className="w-5 h-5" />
            {hasActiveJobs && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
            )}
          </button>

          {/* Custom Actions */}
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      </div>

      {/* Active Job Indicator */}
      {activeJob && (
        <div className="mt-4 px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              <div>
                <p className="text-sm font-medium text-blue-900">
                  {activeJob.type === 'reddit_fetch' && 'Fetching Reddit posts...'}
                  {activeJob.type === 'content_generation' && 'Generating content...'}
                  {activeJob.type === 'notion_sync' && 'Syncing to Notion...'}
                </p>
                <p className="text-xs text-blue-700 mt-0.5">
                  Status: {activeJob.status}
                </p>
              </div>
            </div>
            <button
              onClick={() => useJobStore.getState().setActiveJob(null)}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}
    </header>
  )
}

export default Header
