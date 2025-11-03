import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, TrendingUp, ExternalLink } from 'lucide-react'
import { projectsApi, scansApi } from '../lib/api'

function ScanHistory() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState(() => {
    const saved = localStorage.getItem('asura-selected-project')
    return saved ? Number(saved) : null
  })
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProjects()
  }, [])

  // Persist selected project to localStorage
  useEffect(() => {
    if (selectedProject) {
      localStorage.setItem('asura-selected-project', selectedProject.toString())
      loadScans(selectedProject)
    }
  }, [selectedProject])

  const loadProjects = async () => {
    try {
      const response = await projectsApi.getAll()
      setProjects(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to load projects:', error)
      setLoading(false)
    }
  }

  const loadScans = async (projectId) => {
    try {
      const response = await scansApi.getByProject(projectId)
      setScans(response.data)
    } catch (error) {
      console.error('Failed to load scans:', error)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-100 text-green-800'
      case 'RUNNING':
        return 'bg-blue-100 text-blue-800'
      case 'FAILED':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A'
    if (seconds < 60) return `${seconds.toFixed(0)}s`
    const minutes = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${minutes}m ${secs}s`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-600 border-t-transparent"></div>
      </div>
    )
  }

  if (projects.length === 0) {
    return (
      <div className="card text-center py-12">
        <Clock className="mx-auto text-gray-400 mb-4" size={64} />
        <h3 className="text-xl font-semibold text-gray-700 mb-2">No scan history yet</h3>
        <p className="text-gray-600 mb-6">Create a project and run your first scan to see results here</p>
        <button
          onClick={() => navigate('/projects')}
          className="btn-primary"
        >
          Create Project
        </button>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Scan History</h1>
        <p className="text-gray-600 dark:text-gray-400">Track all your security scans over time</p>
      </div>

      {/* Project Selector */}
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-slate-600 mb-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Select Project
        </label>
        <select
          value={selectedProject || ''}
          onChange={(e) => setSelectedProject(Number(e.target.value))}
          className="w-full md:w-64 px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:focus:ring-blue-500 focus:border-transparent bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
        >
          {projects.map(project => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </select>
      </div>

      {/* Scans Table */}
      {scans.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600">No scans found for this project</p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary mt-4"
          >
            Run First Scan
          </button>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-600 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-slate-700 border-b border-gray-200 dark:border-slate-600">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Scan Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Started
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Issues
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Health Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-slate-800 divide-y divide-gray-200 dark:divide-slate-700">
                {scans.map(scan => (
                  <tr key={scan.id} className="hover:bg-gray-50 dark:hover:bg-slate-700 transition">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {scan.scan_name || `Scan #${scan.id}`}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-600 dark:text-gray-300 capitalize">{scan.scan_type}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(scan.status)}`}>
                        {scan.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                      {new Date(scan.started_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                      {formatDuration(scan.duration_seconds)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-semibold ${
                        scan.total_issues === 0 ? 'text-green-600' :
                        scan.total_issues < 10 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {scan.total_issues}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {scan.health_score !== null ? (
                        <div className="flex items-center gap-2">
                          <TrendingUp
                            size={16}
                            className={
                              scan.health_score >= 80 ? 'text-green-600' :
                              scan.health_score >= 60 ? 'text-yellow-600' :
                              'text-red-600'
                            }
                          />
                          <span className={`text-sm font-semibold ${
                            scan.health_score >= 80 ? 'text-green-600' :
                            scan.health_score >= 60 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {scan.health_score.toFixed(0)}
                          </span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => navigate(`/security/${scan.id}`)}
                        className="text-purple-600 hover:text-purple-800 flex items-center gap-1"
                      >
                        View
                        <ExternalLink size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default ScanHistory
