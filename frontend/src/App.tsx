import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { BrowsePage } from './pages/BrowsePage'
import { GeneratedPage } from './pages/GeneratedPage'
import { NotionPage } from './pages/NotionPage'
import { SettingsPage } from './pages/SettingsPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<BrowsePage />} />
        <Route path="/generated" element={<GeneratedPage />} />
        <Route path="/notion" element={<NotionPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </Layout>
  )
}

export default App
