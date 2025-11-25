import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, Activity, Zap, Target, Play, Clock, CheckCircle, XCircle, AlertTriangle, Plus, Terminal, ChevronRight, Lock } from 'lucide-react'
import { projectsApi, scansApi, default as api } from '../lib/api'
import { useToast } from '../contexts/ToastContext'
import { motion } from 'framer-motion'
import { HealthGauge } from '../components/HealthGauge'
import { SecurityTrendsChart } from '../components/SecurityTrendsChart'
import clsx from 'clsx'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function Dashboard() {
  const navigate = useNavigate()
  const toast = useToast()
  const [projects, setProjects] = useState([])
  const [recentScans, setRecentScans] = useState([])
  const [projectScans, setProjectScans] = useState([])
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
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const projectsRes = await projectsApi.getAll()
      setProjects(projectsRes.data)

      if (projectsRes.data.length > 0) {
        if (!selectedProject) setSelectedProject(projectsRes.data[0].id)
        else await loadProjectStats(selectedProject)
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const loadProjectStats = async (projectId) => {
    try {
      const scansRes = await scansApi.getByProject(projectId)
      const scans = scansRes.data || []
      setProjectScans(scans)
      setRecentScans(scans.slice(0, 5))

      const latestScan = scans.find(s => s.status === 'COMPLETED') || scans[0]
      let criticalCount = 0, highCount = 0, mediumCount = 0, lowCount = 0

      if (latestScan && latestScan.id) {
        try {
          const response = await scansApi.getById(latestScan.id)
          const vulnerabilities = response.data.vulnerabilities || []
          vulnerabilities.forEach(vuln => {
            const s = vuln.severity?.toUpperCase()
            if (s === 'CRITICAL') criticalCount++
            else if (s === 'HIGH') highCount++
            else if (s === 'MEDIUM') mediumCount++
            else if (s === 'LOW') lowCount++
          })
        } catch (err) { console.error(err) }
      }

      const healthScore = latestScan?.health_score ?? 0

      setStats({
        totalProjects: projects.length,
        totalScans: scans.length,
        avgHealthScore: healthScore,
        criticalIssues: criticalCount,
        highIssues: highCount,
        mediumIssues: mediumCount,
        lowIssues: lowCount
      })
    } catch (error) {
      console.error('Failed to load project stats:', error)
    }
  }

  useEffect(() => {
    if (selectedProject) {
      localStorage.setItem('asura-selected-project', selectedProject.toString())
      loadProjectStats(selectedProject)
    }
  }, [selectedProject])

  const startSecurityScan = async () => {
    if (!selectedProject) return
    setIsScanning(true)
    toast.info('Initiating security protocols...')
    try {
      const response = await scansApi.create({
        project_id: selectedProject,
        scan_type: 'security'
      })
      toast.success('Scan started successfully')
      setTimeout(() => navigate(`/security/${response.data.id}`), 1000)
    } catch (error) {
      toast.error('Failed to start scan')
    } finally {
      setIsScanning(false)
    }
  }

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  }

  if (loading && !projects.length) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <Shield className="w-6 h-6 text-primary-500 animate-pulse" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-6"
    >
      {/* Top Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-dark-800/50 p-6 rounded-2xl border border-white/5 backdrop-blur-sm">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <span className="text-primary-400">Welcome back,</span> Parth
          </h1>
          <p className="text-gray-400 text-sm mt-1">System status: <span className="text-green-400 font-mono">ONLINE</span> • {projects.length} Projects Active</p>
        </div>

        <div className="flex items-center gap-4">
          {projects.length > 0 && (
            <div className="relative group">
              <select
                value={selectedProject || ''}
                onChange={(e) => setSelectedProject(Number(e.target.value))}
                className="appearance-none bg-dark-900 border border-white/10 text-white pl-4 pr-10 py-2.5 rounded-xl focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all cursor-pointer min-w-[200px]"
              >
                {projects.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
              <Target className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none group-hover:text-primary-400 transition-colors" />
            </div>
          )}

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={startSecurityScan}
            disabled={!selectedProject || isScanning}
            className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-primary-600 to-primary-500 text-white rounded-xl font-medium shadow-[0_0_20px_rgba(14,165,233,0.3)] hover:shadow-[0_0_30px_rgba(14,165,233,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isScanning ? (
              <RefreshCw className="w-5 h-5 animate-spin" />
            ) : (
              <Play className="w-5 h-5 fill-current" />
            )}
            <span>{isScanning ? 'Scanning...' : 'Start Scan'}</span>
          </motion.button>
        </div>
      </div>

      {projects.length === 0 ? (
        <motion.div variants={item} className="text-center py-20 bg-dark-800/30 rounded-3xl border border-white/5 border-dashed">
          <div className="w-24 h-24 rounded-full bg-primary-500/10 flex items-center justify-center mx-auto mb-6">
            <Shield className="w-12 h-12 text-primary-500" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Initialize Your Workspace</h2>
          <p className="text-gray-400 max-w-md mx-auto mb-8">
            No projects detected. Create your first project to begin security analysis.
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/projects')}
            className="px-8 py-3 bg-white text-dark-900 rounded-xl font-bold hover:bg-gray-100 transition-colors flex items-center gap-2 mx-auto"
          >
            <Plus className="w-5 h-5" />
            Create Project
          </motion.button>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column (Stats & Charts) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Stats Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'Critical', value: stats.criticalIssues, icon: Zap, color: 'text-red-500', bg: 'bg-red-500/10', border: 'border-red-500/20' },
                { label: 'High', value: stats.highIssues, icon: AlertTriangle, color: 'text-orange-500', bg: 'bg-orange-500/10', border: 'border-orange-500/20' },
                { label: 'Medium', value: stats.mediumIssues, icon: Activity, color: 'text-yellow-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' },
                { label: 'Low', value: stats.lowIssues, icon: Shield, color: 'text-blue-500', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  variants={item}
                  className={`p-4 rounded-xl border ${stat.border} ${stat.bg} backdrop-blur-sm relative overflow-hidden group`}
                >
                  <div className="absolute right-0 top-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                    <stat.icon className={`w-12 h-12 ${stat.color}`} />
                  </div>
                  <p className="text-xs font-bold uppercase tracking-wider text-gray-400">{stat.label}</p>
                  <h3 className={`text-2xl font-bold ${stat.color} mt-1`}>{stat.value}</h3>
                </motion.div>
              ))}
            </div>

            {/* Trends Chart */}
            <motion.div variants={item} className="bg-dark-800/50 border border-white/5 rounded-2xl p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-primary-500" />
                  Security Trends
                </h3>
                <span className="text-xs text-gray-500 font-mono">LAST 30 DAYS</span>
              </div>
              <SecurityTrendsChart scans={projectScans} />
            </motion.div>

            {/* Recent Activity (Terminal Style) */}
            <motion.div variants={item} className="bg-dark-900 border border-white/10 rounded-2xl overflow-hidden">
              <div className="bg-dark-800/50 px-4 py-3 border-b border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-gray-400" />
                  <span className="text-sm font-mono text-gray-300">system_logs</span>
                </div>
                <button onClick={() => navigate('/history')} className="text-xs text-primary-400 hover:text-primary-300 transition-colors">
                  View All
                </button>
              </div>
              <div className="p-2 font-mono text-sm">
                {recentScans.length > 0 ? (
                  recentScans.map((scan, i) => (
                    <div
                      key={scan.id}
                      onClick={() => navigate(`/security/${scan.id}`)}
                      className="flex items-center gap-3 p-2 hover:bg-white/5 rounded-lg cursor-pointer transition-colors group"
                    >
                      <span className="text-gray-600 text-xs w-24 shrink-0">{new Date(scan.started_at).toLocaleTimeString()}</span>
                      <span className={clsx(
                        "w-2 h-2 rounded-full shrink-0",
                        scan.status === 'COMPLETED' ? "bg-green-500 shadow-[0_0_5px_rgba(34,197,94,0.5)]" :
                          scan.status === 'FAILED' ? "bg-red-500 shadow-[0_0_5px_rgba(239,68,68,0.5)]" :
                            "bg-yellow-500 animate-pulse"
                      )} />
                      <span className="text-gray-300 group-hover:text-white transition-colors truncate">
                        Scan #{scan.id} initiated on <span className="text-primary-400">{projects.find(p => p.id === scan.project_id)?.name || 'Unknown'}</span>
                      </span>
                      <ChevronRight className="w-4 h-4 text-gray-600 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  ))
                ) : (
                  <div className="p-4 text-gray-500 text-center italic">No recent activity logs.</div>
                )}
              </div>
            </motion.div>
          </div>

          {/* Right Column (Health & Info) */}
          <div className="space-y-6">
            {/* Health Gauge */}
            <motion.div variants={item} className="bg-dark-800/50 border border-white/5 rounded-2xl p-6 backdrop-blur-sm flex flex-col items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-b from-primary-500/5 to-transparent pointer-events-none" />
              <h3 className="text-lg font-bold text-white mb-6 z-10">System Health</h3>
              <HealthGauge score={stats.avgHealthScore} size={220} />
              <div className="mt-6 text-center z-10">
                <p className="text-sm text-gray-400">Security Grade</p>
                <div className={clsx(
                  "text-2xl font-bold mt-1",
                  stats.avgHealthScore >= 90 ? "text-green-400" :
                    stats.avgHealthScore >= 70 ? "text-yellow-400" :
                      "text-red-400"
                )}>
                  {stats.avgHealthScore >= 90 ? 'EXCELLENT' :
                    stats.avgHealthScore >= 70 ? 'GOOD' :
                      stats.avgHealthScore >= 50 ? 'WARNING' : 'CRITICAL'}
                </div>
              </div>
            </motion.div>

            {/* Quick Actions / Info */}
            <motion.div variants={item} className="bg-gradient-to-br from-primary-900/20 to-dark-800/50 border border-primary-500/20 rounded-2xl p-6 relative overflow-hidden">
              <div className="absolute -right-10 -top-10 w-32 h-32 bg-primary-500/20 rounded-full blur-3xl" />
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Lock className="w-5 h-5 text-primary-400" />
                Pro Tips
              </h3>
              <ul className="space-y-3 text-sm text-gray-400">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-primary-500 mt-0.5 shrink-0" />
                  <span>Run scans daily to maintain a high health score.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-primary-500 mt-0.5 shrink-0" />
                  <span>Fix critical issues immediately to prevent breaches.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-primary-500 mt-0.5 shrink-0" />
                  <span>Use .asuraignore to exclude test files.</span>
                </li>
              </ul>
            </motion.div>
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default Dashboard
