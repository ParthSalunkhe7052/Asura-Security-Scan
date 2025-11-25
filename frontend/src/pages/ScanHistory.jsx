import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, TrendingUp, ExternalLink, Search, Filter, ArrowRight, Calendar, Play } from 'lucide-react'
import { projectsApi, scansApi } from '../lib/api'
import Card from '../components/Card'
import Button from '../components/Button'
import Badge from '../components/Badge'
import { useToast } from '../contexts/ToastContext'

function ScanHistory() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState(() => {
    const saved = localStorage.getItem('asura-selected-project')
    return saved ? Number(saved) : null
  })
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const toast = useToast()

  useEffect(() => {
    loadProjects()
  }, [])

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
      toast.error('Failed to load projects')
      setLoading(false)
    }
  }

  const loadScans = async (projectId) => {
    try {
      const response = await scansApi.getByProject(projectId)
      setScans(response.data)
    } catch (error) {
      console.error('Failed to load scans:', error)
      toast.error('Failed to load scans')
    }
  }

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A'
    if (seconds < 60) return `${seconds.toFixed(0)}s`
    const minutes = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${minutes}m ${secs}s`
  }

  const filteredScans = scans.filter(scan =>
    scan.scan_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    scan.status.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Scan History</h1>
          <p className="text-gray-400 mt-1">Track and analyze your security scans over time</p>
        </div>

        {projects.length > 0 && (
          <div className="flex items-center gap-3">
            <select
              value={selectedProject || ''}
              onChange={(e) => setSelectedProject(Number(e.target.value))}
              className="input-field min-w-[200px]"
            >
              <option value="" disabled>Select Project</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {projects.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 text-center border-dashed border-2 border-white/10 bg-transparent">
          <div className="w-20 h-20 rounded-full bg-dark-800 flex items-center justify-center mb-6 border border-white/5">
            <Clock className="w-10 h-10 text-gray-500" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No scan history yet</h3>
          <p className="text-gray-400 max-w-md mb-8">
            Create a project and run your first scan to see results here.
          </p>
          <Button onClick={() => navigate('/projects')} icon={ArrowRight}>
            Create Project
          </Button>
        </Card>
      ) : !selectedProject ? (
        <Card className="text-center py-12">
          <p className="text-gray-400">Select a project to view scan history</p>
        </Card>
      ) : scans.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-gray-400 mb-4">No scans found for this project</p>
          <Button onClick={() => navigate('/')} icon={Play} variant="neon">
            Run First Scan
          </Button>
        </Card>
      ) : (
        <>
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search scans..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-field pl-10"
              />
            </div>
          </div>

          <div className="space-y-4">
            {filteredScans.map(scan => (
              <Card
                key={scan.id}
                className="group hover:border-primary-500/30 transition-all duration-300 cursor-pointer"
                onClick={() => navigate(`/security/${scan.id}`)}
              >
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${scan.status === 'COMPLETED' ? 'bg-green-500/10 text-green-500' :
                        scan.status === 'FAILED' ? 'bg-red-500/10 text-red-500' :
                          'bg-blue-500/10 text-blue-500'
                      }`}>
                      <Clock className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white group-hover:text-primary-400 transition-colors">
                        {scan.scan_name || `Scan #${scan.id}`}
                      </h3>
                      <div className="flex items-center gap-3 text-sm text-gray-500 mt-1">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(scan.started_at).toLocaleString()}
                        </span>
                        <span>•</span>
                        <span>{formatDuration(scan.duration_seconds)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Issues</p>
                      <p className={`font-bold ${scan.total_issues === 0 ? 'text-green-500' :
                          scan.total_issues < 10 ? 'text-yellow-500' :
                            'text-red-500'
                        }`}>
                        {scan.total_issues}
                      </p>
                    </div>

                    <div className="text-center">
                      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Health</p>
                      <div className="flex items-center gap-1">
                        {scan.health_score !== null ? (
                          <>
                            <TrendingUp className={`w-4 h-4 ${scan.health_score >= 80 ? 'text-green-500' :
                                scan.health_score >= 60 ? 'text-yellow-500' :
                                  'text-red-500'
                              }`} />
                            <span className={`font-bold ${scan.health_score >= 80 ? 'text-green-500' :
                                scan.health_score >= 60 ? 'text-yellow-500' :
                                  'text-red-500'
                              }`}>
                              {scan.health_score.toFixed(0)}
                            </span>
                          </>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </div>
                    </div>

                    <div className="w-px h-8 bg-white/10" />

                    <Badge variant={
                      scan.status === 'COMPLETED' ? 'success' :
                        scan.status === 'FAILED' ? 'critical' : 'info'
                    }>
                      {scan.status}
                    </Badge>

                    <ExternalLink className="w-5 h-5 text-gray-500 group-hover:text-white transition-colors" />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default ScanHistory
