import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import RedditPage from './pages/RedditPage'
import PostsPage from './pages/PostsPage'
import NotionPage from './pages/NotionPage'
import SettingsPage from './pages/SettingsPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="reddit" element={<RedditPage />} />
          <Route path="posts" element={<PostsPage />} />
          <Route path="notion" element={<NotionPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
