import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Database,
  Settings,
  Rss,
} from 'lucide-react'
import { useCategoryStore } from '@/store/useCategoryStore'
import { useEffect } from 'react'

const Sidebar = () => {
  const { categories, fetchCategories } = useCategoryStore()

  useEffect(() => {
    fetchCategories()
  }, [fetchCategories])

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/reddit', icon: Rss, label: 'Reddit Browser' },
    { to: '/posts', icon: FileText, label: 'Posts' },
    { to: '/notion', icon: Database, label: 'Notion Sync' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col h-screen">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-xl font-bold">LinkedIn Automation</h1>
        <p className="text-sm text-gray-400 mt-1">Content Studio</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <div className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        {/* Categories Section */}
        {categories.length > 0 && (
          <div className="mt-8">
            <h3 className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              Categories
            </h3>
            <div className="space-y-1">
              {categories.map((category) => (
                <NavLink
                  key={category.id}
                  to={`/posts?category=${category.id}`}
                  className="flex items-center gap-3 px-4 py-2 rounded-lg text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
                >
                  <div className="w-2 h-2 rounded-full bg-primary-500" />
                  <span>{category.name}</span>
                </NavLink>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-500">
          <p>Version 1.0.0</p>
          <p className="mt-1">© 2024 Content Studio</p>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
