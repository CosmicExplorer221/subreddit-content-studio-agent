// Layout Component with Sidebar Navigation
import { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { Train, FileText, Sparkles, Send, Settings } from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-railway-800 text-white flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-railway-700">
          <div className="flex items-center gap-3">
            <Train className="w-8 h-8" />
            <div>
              <h1 className="text-xl font-bold">Content Studio</h1>
              <p className="text-sm text-railway-300">Railway Edition</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
                isActive
                  ? 'bg-railway-700 text-white'
                  : 'text-railway-200 hover:bg-railway-700/50'
              }`
            }
          >
            <FileText className="w-5 h-5" />
            <span>Browse Posts</span>
          </NavLink>

          <NavLink
            to="/generated"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
                isActive
                  ? 'bg-railway-700 text-white'
                  : 'text-railway-200 hover:bg-railway-700/50'
              }`
            }
          >
            <Sparkles className="w-5 h-5" />
            <span>Generated Content</span>
          </NavLink>

          <NavLink
            to="/notion"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
                isActive
                  ? 'bg-railway-700 text-white'
                  : 'text-railway-200 hover:bg-railway-700/50'
              }`
            }
          >
            <Send className="w-5 h-5" />
            <span>Notion Sync</span>
          </NavLink>

          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
                isActive
                  ? 'bg-railway-700 text-white'
                  : 'text-railway-200 hover:bg-railway-700/50'
              }`
            }
          >
            <Settings className="w-5 h-5" />
            <span>Settings</span>
          </NavLink>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-railway-700 text-sm text-railway-300">
          <p>Version 1.0.0</p>
          <p>Built with AI</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
    </div>
  )
}
