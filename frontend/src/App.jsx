import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import SecurityResults from './pages/SecurityResults'
import Projects from './pages/Projects'
import ScanHistory from './pages/ScanHistory'
import Metrics from './pages/Metrics'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/security/:scanId" element={<SecurityResults />} />
        <Route path="/history" element={<ScanHistory />} />
        <Route path="/metrics/:projectId" element={<Metrics />} />
      </Routes>
    </Layout>
  )
}

export default App
