import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { BarChart3, TrendingUp, Shield, Activity, FileCode, Download } from 'lucide-react'

const API_BASE = 'http://localhost:8000'

function Metrics() {
  const { projectId } = useParams()
  const [project, setProject] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [computing, setComputing] = useState(false)

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
    } catch (error) {
      console.error('Error computing metrics:', error)
      alert('Failed to compute metrics')
    } finally {
      setComputing(false)
    }
  }

  const exportMetrics = () => {
    window.open(`${API_BASE}/api/reports/export/${projectId}?format=json`, '_blank')
  }

  const getGradeColor = (grade) => {
    const colors = {
      A: 'text-green-600 bg-green-50 border-green-200',
      B: 'text-blue-600 bg-blue-50 border-blue-200',
      C: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      D: 'text-orange-600 bg-orange-50 border-orange-200',
      F: 'text-red-600 bg-red-50 border-red-200'
    }
    return colors[grade] || colors.F
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
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

  const getScoreDescription = (score) => {
    if (score >= 90) return '🎯 Exceptional'
    if (score >= 80) return '✨ Excellent'
    if (score >= 70) return '👍 Good'
    if (score >= 60) return '⚠️ Fair'
    if (score >= 50) return '⚡ Needs Work'
    return '🚨 Critical'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
            <BarChart3 className="w-8 h-8 mr-3 text-blue-600" />
            Code Metrics
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Project: {project?.name}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={computeMetrics}
            disabled={computing}
            className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
              computing
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            {computing ? 'Computing...' : 'Recompute Metrics'}
          </button>
          <button
            onClick={exportMetrics}
            className="flex items-center px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 dark:bg-slate-800 dark:text-white transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Code Health Score Card */}
      {metrics?.health && (
        <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-8 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">Code Health Score</h2>
              <p className="text-indigo-100">
                Weighted score based on security and coverage metrics
              </p>
            </div>
            <div className="text-center">
              <div className="text-sm font-semibold mb-1 text-indigo-200">
                {getScoreDescription(metrics.health.code_health_score)}
              </div>
              <div className="text-6xl font-bold mb-2">
                {metrics.health.code_health_score.toFixed(1)}
              </div>
              <div className={`inline-block px-6 py-3 rounded-full text-xl font-bold border-2 ${getGradeColor(metrics.health.grade)}`}>
                {getGradeDescription(metrics.health.grade).emoji} {getGradeDescription(metrics.health.grade).label} ({metrics.health.grade})
              </div>
              <div className="text-sm text-indigo-200 mt-2">
                {getGradeDescription(metrics.health.grade).description}
              </div>
            </div>
          </div>
          
          {/* Score Breakdown */}
          <div className="mt-6 grid grid-cols-2 gap-4">
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <div className="flex items-center mb-2">
                <Shield className="w-5 h-5 mr-2" />
                <span className="font-semibold">Security</span>
              </div>
              <div className="text-3xl font-bold">{metrics.health.security_score.toFixed(1)}</div>
              <div className="text-sm text-indigo-100">50% weight</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <div className="flex items-center mb-2">
                <FileCode className="w-5 h-5 mr-2" />
                <span className="font-semibold">Coverage</span>
              </div>
              <div className="text-3xl font-bold">{metrics.health.coverage_score.toFixed(1)}%</div>
              <div className="text-sm text-indigo-100">50% weight</div>
            </div>
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Security Metrics */}
        {metrics?.security && (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-slate-600 p-6">
            <div className="flex items-center mb-4">
              <Shield className="w-6 h-6 text-red-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Security</h3>
            </div>
            <div className={`text-4xl font-bold mb-2 ${getScoreColor(metrics.security.score)}`}>
              {metrics.security.score.toFixed(1)}
            </div>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
              <div className="flex justify-between">
                <span>Total Issues:</span>
                <span className="font-semibold text-gray-900 dark:text-white">{metrics.security.total_issues}</span>
              </div>
              {metrics.security.last_scan && (
                <div className="flex justify-between">
                  <span>Last Scan:</span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {new Date(metrics.security.last_scan).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Coverage Metrics */}
        {metrics?.coverage && (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-slate-600 p-6">
            <div className="flex items-center mb-4">
              <FileCode className="w-6 h-6 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Test Coverage</h3>
            </div>
            <div className={`text-4xl font-bold mb-2 ${getScoreColor(metrics.coverage.coverage_percent)}`}>
              {metrics.coverage.coverage_percent.toFixed(1)}%
            </div>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
              <div className="flex justify-between">
                <span>Lines Covered:</span>
                <span className="font-semibold text-gray-900 dark:text-white">{metrics.coverage.lines_covered}</span>
              </div>
              <div className="flex justify-between">
                <span>Total Lines:</span>
                <span className="font-semibold text-gray-900 dark:text-white">{metrics.coverage.lines_total}</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-2 mt-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${metrics.coverage.coverage_percent}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Complexity Analysis */}
      {metrics?.complexity && (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-slate-600">
          <div className="p-6 border-b border-gray-200 dark:border-slate-600">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Complexity Analysis</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
              Cyclomatic complexity by file
            </p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4">
                <div className="text-sm text-blue-600 dark:text-blue-400 font-medium mb-1">Average Complexity</div>
                <div className="text-3xl font-bold text-blue-900 dark:text-blue-300">
                  {metrics.complexity.average_complexity.toFixed(2)}
                </div>
              </div>
              <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-4">
                <div className="text-sm text-green-600 dark:text-green-400 font-medium mb-1">Files Analyzed</div>
                <div className="text-3xl font-bold text-green-900 dark:text-green-300">
                  {metrics.complexity.files_analyzed}
                </div>
              </div>
            </div>

            {/* Complexity per file */}
            {metrics.complexity.files && Object.keys(metrics.complexity.files).length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 dark:bg-slate-700">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">File</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Complexity</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Functions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-slate-700">
                    {Object.entries(metrics.complexity.files).slice(0, 10).map(([file, data]) => (
                      <tr key={file} className="hover:bg-gray-50 dark:hover:bg-slate-700">
                        <td className="px-4 py-2 text-sm font-mono text-gray-900 dark:text-gray-300">{file}</td>
                        <td className="px-4 py-2">
                          <span className={`text-sm font-semibold ${
                            data.complexity > 10 ? 'text-red-600' :
                            data.complexity > 5 ? 'text-yellow-600' :
                            'text-green-600'
                          }`}>
                            {data.complexity.toFixed(2)}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300">
                          {data.functions?.length || 0}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default Metrics
