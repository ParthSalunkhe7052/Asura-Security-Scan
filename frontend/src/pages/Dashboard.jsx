import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, Activity, FileSearch, TrendingUp, AlertTriangle, BarChart3, Play, CheckCircle, XCircle, Clock, Target, Zap, Award, RefreshCw } from 'lucide-react'
import { projectsApi, scansApi } from '../lib/api'
import axios from 'axios'
import { useToast } from '../contexts/ToastContext'
import { DashboardSkeleton, StatCardSkeleton } from '../components/LoadingSkeleton'
import { EmptyState } from '../components/EmptyState'
import { CommandPalette } from '../components/CommandPalette'

function Dashboard() {
  const navigate = useNavigate()
  const toast = useToast()
  const [projects, setProjects] = useState([])
  const [recentScans, setRecentScans] = useState([])
  const [stats, setStats] = useState({
    totalProjects: 0,
    totalScans: 0,
    avgHealthScore: 0,
    criticalIssues: 0,
    highIssues: 0,
    mediumIssues: 0,
    lowIssues: 0
  })
  const [selectedProject, setSelectedProject] = useState(() => {
    const saved = localStorage.getItem('asura-selected-project')
    return saved ? Number(saved) : null
  })
  const [isScanning, setIsScanning] = useState(false)
  const [projectMetrics, setProjectMetrics] = useState(null)
  const [severityBreakdown, setSeverityBreakdown] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return
    
    const interval = setInterval(() => {
      loadDashboardData()
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [autoRefresh, selectedProject])

  const loadDashboardData = async (showToast = false) => {
    try {
      setLoading(true)
      const projectsRes = await projectsApi.getAll()
      setProjects(projectsRes.data)
      
      // Don't auto-select project - user must choose
      if (projectsRes.data.length === 0) {
        setStats({
          totalProjects: 0,
          totalScans: 0,
          avgHealthScore: 0,
          criticalIssues: 0,
          highIssues: 0,
          mediumIssues: 0,
          lowIssues: 0
        })
      }
      setLastUpdated(new Date())
      if (showToast) {
        toast.success('Dashboard refreshed successfully!')
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadDashboardData(true)
  }

  const loadProjectStats = async (projectId) => {
    try {
      // Load scans for the selected project
      const scansRes = await scansApi.getByProject(projectId)
      const scans = scansRes.data || []
      setRecentScans(scans.slice(0, 5))
      
      // Get latest completed scan
      const latestScan = scans.find(s => s.status === 'COMPLETED') || scans[0]
      
      // Calculate severity breakdown from latest scan
      let criticalCount = 0
      let highCount = 0
      let mediumCount = 0
      let lowCount = 0
      
      if (latestScan && latestScan.id) {
        try {
          const response = await axios.get(`http://localhost:8000/api/scans/${latestScan.id}/vulnerabilities`)
          const vulnerabilities = response.data || []
          
          vulnerabilities.forEach(vuln => {
            const severity = vuln.severity?.toUpperCase()
            if (severity === 'CRITICAL') criticalCount++
            else if (severity === 'HIGH') highCount++
            else if (severity === 'MEDIUM') mediumCount++
            else if (severity === 'LOW') lowCount++
          })
        } catch (err) {
          console.error('Failed to load vulnerabilities:', err)
        }
      }
      
      setSeverityBreakdown({
        critical: criticalCount,
        high: highCount,
        medium: mediumCount,
        low: lowCount
      })
      
      // Try to load metrics
      try {
        const metricsRes = await axios.get(`http://localhost:8000/api/metrics/${projectId}`)
        setProjectMetrics(metricsRes.data)
      } catch (err) {
        console.log('Metrics not yet available for project')
        setProjectMetrics(null)
      }
      
      // Update stats
      setStats({
        totalProjects: projects.length || 1,
        totalScans: scans.length,
        avgHealthScore: projectMetrics?.health?.code_health_score || 0,
        criticalIssues: criticalCount,
        highIssues: highCount,
        mediumIssues: mediumCount,
        lowIssues: lowCount
      })
    } catch (error) {
      console.error('Failed to load project stats:', error)
    }
  }

  // Persist selected project to localStorage
  useEffect(() => {
    if (selectedProject) {
      localStorage.setItem('asura-selected-project', selectedProject.toString())
      loadProjectStats(selectedProject)
    }
  }, [selectedProject])

  const startSecurityScan = async () => {
    if (!selectedProject) {
      alert('Please select a project first')
      return
    }

    setIsScanning(true)
    toast.info('Starting security scan...')
    try {
      const response = await scansApi.create({
        project_id: selectedProject,
        scan_type: 'security'
      })
      
      toast.success('Security scan started successfully!')
      
      // Navigate to scan results page
      setTimeout(() => {
        navigate(`/security/${response.data.id}`)
      }, 1000)
    } catch (error) {
      console.error('Failed to start scan:', error)
      toast.error('Failed to start security scan')
    } finally {
      setIsScanning(false)
    }
  }

  const viewMetrics = () => {
    if (!selectedProject) {
      alert('Please select a project first')
      return
    }
    navigate(`/metrics/${selectedProject}`)
  }

  if (loading) {
    return <DashboardSkeleton />
  }

  return (
    <div>
      <CommandPalette 
        projects={projects}
        onStartScan={startSecurityScan}
        onViewMetrics={viewMetrics}
      />
      
      {/* Refresh Controls */}
      {projects.length > 0 && (
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-700 rounded-lg border border-gray-300 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-600 transition-all disabled:opacity-50 font-medium dark:text-white"
            >
              <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
              <span className="text-sm font-medium">{refreshing ? 'Refreshing...' : 'Refresh'}</span>
            </button>
            
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="w-4 h-4 text-purple-600 rounded"
              />
              <span className="text-sm text-gray-700">Auto-refresh (30s)</span>
            </label>
          </div>
          
          {lastUpdated && (
            <p className="text-xs text-gray-500">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>
      )}
      {/* Project Health Banner - Replaces Quick Overview */}
      {projects.length > 0 && projectMetrics && (
        <div className="mb-6 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-xl overflow-hidden shadow-lg">
          <div className="p-6 text-white">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Award size={32} />
                <div>
                  <h2 className="text-2xl font-bold">Project Health</h2>
                  <p className="text-indigo-100 text-sm">{projects.find(p => p.id === selectedProject)?.name}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-5xl font-bold">{projectMetrics.health?.code_health_score?.toFixed(0) || 0}</div>
                <div className="text-lg font-semibold mt-1">Grade {projectMetrics.health?.grade || 'N/A'}</div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white/10 backdrop-blur rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Shield size={16} />
                  <span className="text-sm font-medium">Security</span>
                </div>
                <div className="text-2xl font-bold">{projectMetrics.health?.security_score?.toFixed(0) || 0}</div>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Target size={16} />
                  <span className="text-sm font-medium">Coverage</span>
                </div>
                <div className="text-2xl font-bold">{projectMetrics.coverage?.coverage_percent?.toFixed(0) || 0}%</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm hover:shadow-md transition-all border-2 border-gray-100 dark:border-slate-600 cursor-pointer hover:border-blue-300 dark:hover:border-blue-500">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
              <FileSearch className="text-blue-600 dark:text-blue-400" size={20} />
            </div>
            <p className="text-xs font-semibold text-gray-500 uppercase">Total Scans</p>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.totalScans}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">For this project</p>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm hover:shadow-md transition-all border-2 border-red-200 dark:border-red-900/50 cursor-pointer hover:border-red-300 dark:hover:border-red-700 bg-gradient-to-br from-red-50 dark:from-red-900/20 to-white dark:to-slate-800">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-red-100 dark:bg-red-900/50 rounded-lg">
              <AlertTriangle className="text-red-600 dark:text-red-400" size={20} />
            </div>
            <p className="text-xs font-semibold text-gray-500 uppercase">Critical</p>
          </div>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400">{stats.criticalIssues}</p>
          <p className="text-xs text-red-600 mt-1 font-medium">Needs attention</p>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm hover:shadow-md transition-all border-2 border-orange-200 dark:border-orange-900/50 cursor-pointer hover:border-orange-300 dark:hover:border-orange-700">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-orange-100 dark:bg-orange-900/50 rounded-lg">
              <Zap className="text-orange-600 dark:text-orange-400" size={20} />
            </div>
            <p className="text-xs font-semibold text-gray-500 uppercase">High</p>
          </div>
          <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">{stats.highIssues}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Priority issues</p>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm hover:shadow-md transition-all border-2 border-yellow-200 dark:border-yellow-900/50 cursor-pointer hover:border-yellow-300 dark:hover:border-yellow-700">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900/50 rounded-lg">
              <Activity className="text-yellow-600 dark:text-yellow-400" size={20} />
            </div>
            <p className="text-xs font-semibold text-gray-500 uppercase">Medium</p>
          </div>
          <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{stats.mediumIssues}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Review later</p>
        </div>
      </div>

      {/* Vulnerability Severity Breakdown */}
      {projects.length > 0 && severityBreakdown && (
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-slate-600 mb-6 transition-colors">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Target size={20} className="text-purple-600" />
            Vulnerability Distribution
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                <div className="w-2 h-2 rounded-full bg-red-500"></div>
                <span className="text-sm font-medium text-gray-700">Critical</span>
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden mx-3">
                  <div 
                    className="h-full bg-red-500 rounded-full transition-all duration-500"
                    style={{ width: `${severityBreakdown.critical > 0 ? Math.min((severityBreakdown.critical / (severityBreakdown.critical + severityBreakdown.high + severityBreakdown.medium + severityBreakdown.low)) * 100, 100) : 0}%` }}
                  ></div>
                </div>
              </div>
              <span className="text-sm font-bold text-red-600 w-12 text-right">{severityBreakdown.critical}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                <span className="text-sm font-medium text-gray-700">High</span>
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden mx-3">
                  <div 
                    className="h-full bg-orange-500 rounded-full transition-all duration-500"
                    style={{ width: `${severityBreakdown.high > 0 ? Math.min((severityBreakdown.high / (severityBreakdown.critical + severityBreakdown.high + severityBreakdown.medium + severityBreakdown.low)) * 100, 100) : 0}%` }}
                  ></div>
                </div>
              </div>
              <span className="text-sm font-bold text-orange-600 w-12 text-right">{severityBreakdown.high}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                <span className="text-sm font-medium text-gray-700">Medium</span>
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden mx-3">
                  <div 
                    className="h-full bg-yellow-500 rounded-full transition-all duration-500"
                    style={{ width: `${severityBreakdown.medium > 0 ? Math.min((severityBreakdown.medium / (severityBreakdown.critical + severityBreakdown.high + severityBreakdown.medium + severityBreakdown.low)) * 100, 100) : 0}%` }}
                  ></div>
                </div>
              </div>
              <span className="text-sm font-bold text-yellow-600 w-12 text-right">{severityBreakdown.medium}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                <span className="text-sm font-medium text-gray-700">Low</span>
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden mx-3">
                  <div 
                    className="h-full bg-blue-500 rounded-full transition-all duration-500"
                    style={{ width: `${severityBreakdown.low > 0 ? Math.min((severityBreakdown.low / (severityBreakdown.critical + severityBreakdown.high + severityBreakdown.medium + severityBreakdown.low)) * 100, 100) : 0}%` }}
                  ></div>
                </div>
              </div>
              <span className="text-sm font-bold text-blue-600 w-12 text-right">{severityBreakdown.low}</span>
            </div>
          </div>
        </div>
      )}

      {/* Project Selector */}
      {projects.length > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-6 shadow-sm border-2 border-purple-200 mb-6">
          <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
            <Target size={18} className="text-purple-600" />
            Select Project
          </label>
          <select
            value={selectedProject || ''}
            onChange={(e) => setSelectedProject(e.target.value ? Number(e.target.value) : null)}
            className="w-full px-4 py-3 border-2 border-purple-200 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-purple-500 dark:focus:ring-blue-500 focus:border-purple-500 dark:focus:border-blue-400 transition-all font-semibold text-lg bg-white dark:bg-slate-800 dark:text-white"
          >
            <option value="">-- Select a project to view stats --</option>
            {projects.map(project => (
              <option key={project.id} value={project.id}>
                📁 {project.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Quick Actions - Separated */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Security Scan Card */}
        <div className="bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-900/30 dark:to-slate-900 rounded-xl p-6 shadow-sm hover:shadow-lg transition-all border-2 border-red-200 dark:border-red-900/50">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-red-500 dark:bg-red-600 rounded-xl shadow-lg">
              <Shield className="text-white" size={28} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">Security Scan</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Find vulnerabilities</p>
            </div>
          </div>
          
          {projects.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">Create a project first</p>
              <button
                onClick={() => navigate('/projects')}
                className="px-4 py-2 bg-red-500 dark:bg-red-600 text-white rounded-lg hover:bg-red-600 dark:hover:bg-red-500 transition-colors w-full font-medium"
              >
                Create Project
              </button>
            </div>
          ) : (
            <button
              onClick={startSecurityScan}
              disabled={isScanning}
              className="w-full mt-4 px-6 py-3 bg-red-500 dark:bg-red-600 text-white rounded-xl hover:bg-red-600 dark:hover:bg-red-500 disabled:bg-gray-400 dark:disabled:bg-slate-600 transition-all font-semibold shadow-md hover:shadow-lg flex items-center justify-center gap-2"
            >
              {isScanning ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  Scanning...
                </>
              ) : (
                <>
                  <Play size={20} />
                  Start Scan
                </>
              )}
            </button>
          )}
        </div>

        {/* Metrics Card */}
        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/30 dark:to-slate-900 rounded-xl p-6 shadow-sm hover:shadow-lg transition-all border-2 border-blue-200 dark:border-blue-900/50">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-blue-500 dark:bg-blue-600 rounded-xl shadow-lg">
              <BarChart3 className="text-white" size={28} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">Code Metrics</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Quality insights</p>
            </div>
          </div>
          
          {projects.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">Create a project first</p>
              <button
                onClick={() => navigate('/projects')}
                className="px-4 py-2 bg-blue-500 dark:bg-blue-600 text-white rounded-lg hover:bg-blue-600 dark:hover:bg-blue-500 transition-colors w-full font-medium"
              >
                Create Project
              </button>
            </div>
          ) : (
            <button
              onClick={viewMetrics}
              disabled={!selectedProject}
              className="w-full mt-4 px-6 py-3 bg-blue-500 dark:bg-blue-600 text-white rounded-xl hover:bg-blue-600 dark:hover:bg-blue-500 disabled:bg-gray-400 dark:disabled:bg-slate-600 transition-all font-semibold shadow-md hover:shadow-lg flex items-center justify-center gap-2"
            >
              <BarChart3 size={20} />
              View Metrics
            </button>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      {recentScans.length > 0 ? (
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-slate-600 transition-colors">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2 dark:text-white">
            <Clock size={24} className="text-gray-600" />
            Recent Activity
          </h2>
          
          <div className="space-y-3">
            {recentScans.map(scan => (
              <div
                key={scan.id}
                onClick={() => navigate(`/security/${scan.id}`)}
                className="p-4 border-2 border-gray-100 dark:border-slate-600 rounded-xl hover:border-purple-300 dark:hover:border-blue-500 hover:bg-purple-50 dark:hover:bg-slate-700 cursor-pointer transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      scan.status === 'COMPLETED' ? 'bg-green-100 dark:bg-green-900' :
                      scan.status === 'FAILED' ? 'bg-red-100 dark:bg-red-900' :
                      'bg-yellow-100 dark:bg-yellow-900'
                    }`}>
                      {scan.status === 'COMPLETED' ? <CheckCircle className="text-green-600" size={20} /> :
                       scan.status === 'FAILED' ? <XCircle className="text-red-600" size={20} /> :
                       <Clock className="text-yellow-600" size={20} />}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-blue-300 transition-colors">
                        {scan.scan_name || `Security Scan #${scan.id}`}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(scan.started_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    {scan.total_issues !== undefined && (
                      <span className="px-3 py-1 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg text-sm font-medium">
                        {scan.total_issues} issues
                      </span>
                    )}
                    <span className={`px-3 py-1 rounded-lg text-sm font-medium ${
                      scan.status === 'COMPLETED' ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300' :
                      scan.status === 'FAILED' ? 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300' :
                      'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300'
                    }`}>
                      {scan.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : projects.length > 0 ? (
        <EmptyState 
          type="scans" 
          onAction={startSecurityScan}
          actionLabel="Start First Scan"
        />
      ) : null}

      {/* Welcome Card for New Users */}
      {projects.length === 0 && (
        <div className="bg-gradient-to-br from-purple-500 to-indigo-600 dark:from-slate-800 dark:to-slate-700 rounded-2xl p-8 text-white shadow-2xl border-2 dark:border-blue-500">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-4 bg-white/20 rounded-2xl backdrop-blur">
              <Shield size={48} />
            </div>
            <div>
              <h2 className="text-3xl font-bold mb-2">Welcome to ASURA! 🔥</h2>
              <p className="text-purple-100 dark:text-gray-400">Your AI-powered security companion</p>
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 mb-6">
            <p className="text-lg mb-4">
              Get started by creating your first project. ASURA provides:
            </p>
            <ul className="space-y-2">
              <li className="flex items-center gap-3">
                <CheckCircle size={20} className="text-green-300" />
                <span>🔒 Security vulnerability scanning (Bandit, Safety, Semgrep)</span>
              </li>
              <li className="flex items-center gap-3">
                <CheckCircle size={20} className="text-green-300" />
                <span>📊 Code quality metrics and health scores</span>
              </li>
              <li className="flex items-center gap-3">
                <CheckCircle size={20} className="text-green-300" />
                <span>📈 Beautiful reports and insights</span>
              </li>
            </ul>
          </div>
          
          <button
            onClick={() => navigate('/projects')}
            className="px-8 py-4 bg-white dark:bg-blue-600 text-purple-600 dark:text-white rounded-xl hover:bg-purple-50 dark:hover:bg-blue-500 transition-all font-bold text-lg shadow-xl hover:shadow-2xl flex items-center gap-3"
          >
            <Play size={24} />
            Create Your First Project
          </button>
        </div>
      )}
    </div>
  )
}

export default Dashboard
