import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { BarChart3, TrendingUp, Shield, Activity, FileCode, Download, RefreshCw, Zap, Target, Layers } from 'lucide-react'
import Card from '../components/Card'
import Button from '../components/Button'
import Badge from '../components/Badge'
import { useToast } from '../contexts/ToastContext'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function Metrics() {
  const { projectId } = useParams()
  const [project, setProject] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [computing, setComputing] = useState(false)
  const toast = useToast()

  useEffect(() => {
    if (projectId) {
      loadMetrics()
    }
  }, [projectId])

  const loadMetrics = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/metrics/${projectId}`)
      const data = await response.json()
      setProject({ id: projectId, name: data.project_name })
      setMetrics(data)
      setLoading(false)
    } catch (error) {
      console.error('Error loading metrics:', error)
      toast.error('Failed to load metrics')
      setLoading(false)
    }
  }

  const computeMetrics = async () => {
    setComputing(true)
    try {
      const response = await fetch(`${API_BASE}/api/metrics/${projectId}/compute`, {
        method: 'POST'
      })
      const data = await response.json()
      setMetrics(data)
      toast.success('Metrics recomputed successfully')
    } catch (error) {
      console.error('Error computing metrics:', error)
      toast.error('Failed to compute metrics')
    } finally {
      setComputing(false)
    }
  }

  const exportMetrics = () => {
    window.open(`${API_BASE}/api/reports/export/${projectId}?format=json`, '_blank')
  }

  const getGradeColor = (grade) => {
    const colors = {
      A: 'text-green-400 border-green-500/50 bg-green-500/10',
      B: 'text-blue-400 border-blue-500/50 bg-blue-500/10',
      C: 'text-yellow-400 border-yellow-500/50 bg-yellow-500/10',
      D: 'text-orange-400 border-orange-500/50 bg-orange-500/10',
      F: 'text-red-400 border-red-500/50 bg-red-500/10'
    }
    return colors[grade] || colors.F
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getGradeDescription = (grade) => {
    const descriptions = {
      A: { label: 'Excellent', description: 'Outstanding code quality', emoji: '🎯' },
      B: { label: 'Good', description: 'Solid code quality', emoji: '✨' },
      C: { label: 'Fair', description: 'Needs improvement', emoji: '👍' },
      D: { label: 'Poor', description: 'Significant issues', emoji: '⚠️' },
      F: { label: 'Critical', description: 'Urgent action needed', emoji: '🚨' }
    }
    return descriptions[grade] || descriptions.F
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-primary-500" />
            Code Metrics
          </h1>
          <p className="text-gray-400 mt-1">
            Detailed analysis for <span className="text-white font-medium">{project?.name}</span>
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            onClick={computeMetrics}
            isLoading={computing}
            variant="neon"
            icon={RefreshCw}
          >
            Recompute
          </Button>
          <Button
            onClick={exportMetrics}
            variant="secondary"
            icon={Download}
          >
            Export
          </Button>
        </div>
      </div>

      {/* Code Health Score Card */}
      {metrics?.health && (
        <Card className="relative overflow-hidden border-primary-500/30 bg-gradient-to-br from-primary-900/20 to-purple-900/20">
          <div className="absolute top-0 right-0 p-8 opacity-10">
            <Activity size={150} />
          </div>

          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8 p-4">
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-2">Code Health Score</h2>
              <p className="text-gray-300 max-w-md">
                A comprehensive rating based on security vulnerabilities, test coverage, and code complexity.
              </p>

              <div className="mt-6 flex gap-4">
                <div className="bg-dark-900/50 rounded-xl p-4 border border-white/10 flex-1">
                  <div className="flex items-center gap-2 mb-1 text-gray-400 text-sm">
                    <Shield size={14} /> Security
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {metrics.health.security_score.toFixed(1)}
                  </div>
                </div>
                <div className="bg-dark-900/50 rounded-xl p-4 border border-white/10 flex-1">
                  <div className="flex items-center gap-2 mb-1 text-gray-400 text-sm">
                    <Target size={14} /> Coverage
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {metrics.health.coverage_score.toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            <div className="text-center">
              <div className={`inline-flex flex-col items-center justify-center w-40 h-40 rounded-full border-4 ${getGradeColor(metrics.health.grade)} bg-dark-900/50 backdrop-blur-xl shadow-[0_0_30px_rgba(0,0,0,0.3)]`}>
                <span className="text-5xl font-bold text-white mb-1">
                  {metrics.health.code_health_score.toFixed(0)}
                </span>
                <span className={`text-lg font-bold px-3 py-0.5 rounded-full ${getGradeColor(metrics.health.grade)}`}>
                  Grade {metrics.health.grade}
                </span>
              </div>
              <p className="mt-4 text-lg font-medium text-white">
                {getGradeDescription(metrics.health.grade).emoji} {getGradeDescription(metrics.health.grade).label}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Security Metrics */}
        {metrics?.security && (
          <Card className="h-full">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-red-500/10 rounded-xl border border-red-500/20">
                <Shield className="w-6 h-6 text-red-500" />
              </div>
              <h3 className="text-xl font-bold text-white">Security</h3>
            </div>

            <div className="flex items-end gap-2 mb-6">
              <span className={`text-5xl font-bold ${getScoreColor(metrics.security.score)}`}>
                {metrics.security.score.toFixed(1)}
              </span>
              <span className="text-gray-500 mb-2">/ 100</span>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                <span className="text-gray-400">Total Issues</span>
                <span className="font-bold text-white">{metrics.security.total_issues}</span>
              </div>
              {metrics.security.last_scan && (
                <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-400">Last Scan</span>
                  <span className="font-mono text-sm text-white">
                    {new Date(metrics.security.last_scan).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Coverage Metrics */}
        {metrics?.coverage && (
          <Card className="h-full">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
                <FileCode className="w-6 h-6 text-blue-500" />
              </div>
              <h3 className="text-xl font-bold text-white">Test Coverage</h3>
            </div>

            <div className="flex items-end gap-2 mb-6">
              <span className={`text-5xl font-bold ${getScoreColor(metrics.coverage.coverage_percent)}`}>
                {metrics.coverage.coverage_percent.toFixed(1)}%
              </span>
            </div>

            <div className="space-y-4">
              <div className="w-full bg-dark-900 rounded-full h-3 overflow-hidden border border-white/5">
                <div
                  className="bg-blue-500 h-full rounded-full transition-all duration-1000"
                  style={{ width: `${metrics.coverage.coverage_percent}%` }}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-white/5 rounded-lg text-center">
                  <p className="text-xs text-gray-400 uppercase mb-1">Lines Covered</p>
                  <p className="font-bold text-white">{metrics.coverage.lines_covered}</p>
                </div>
                <div className="p-3 bg-white/5 rounded-lg text-center">
                  <p className="text-xs text-gray-400 uppercase mb-1">Total Lines</p>
                  <p className="font-bold text-white">{metrics.coverage.lines_total}</p>
                </div>
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Complexity Analysis */}
      {metrics?.complexity && (
        <Card>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-purple-500/10 rounded-xl border border-purple-500/20">
              <Layers className="w-6 h-6 text-purple-500" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Complexity Analysis</h3>
              <p className="text-gray-400 text-sm">Cyclomatic complexity breakdown</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div className="bg-dark-900/50 rounded-xl p-4 border border-white/5">
              <div className="text-sm text-gray-400 font-medium mb-1">Average Complexity</div>
              <div className="text-3xl font-bold text-white">
                {metrics.complexity.average_complexity.toFixed(2)}
              </div>
            </div>
            <div className="bg-dark-900/50 rounded-xl p-4 border border-white/5">
              <div className="text-sm text-gray-400 font-medium mb-1">Files Analyzed</div>
              <div className="text-3xl font-bold text-white">
                {metrics.complexity.files_analyzed}
              </div>
            </div>
          </div>

          {/* Complexity per file */}
          {metrics.complexity.files && Object.keys(metrics.complexity.files).length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="px-4 py-3 text-xs font-medium text-gray-400 uppercase">File</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-400 uppercase">Complexity</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-400 uppercase">Functions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {Object.entries(metrics.complexity.files).slice(0, 10).map(([file, data]) => (
                    <tr key={file} className="hover:bg-white/5 transition-colors">
                      <td className="px-4 py-3 text-sm font-mono text-gray-300">{file}</td>
                      <td className="px-4 py-3">
                        <Badge variant={
                          data.complexity > 10 ? 'critical' :
                            data.complexity > 5 ? 'medium' : 'success'
                        }>
                          {data.complexity.toFixed(2)}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-400">
                        {data.functions?.length || 0}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}

export default Metrics
