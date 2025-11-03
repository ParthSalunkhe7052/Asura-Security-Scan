import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, AlertTriangle, Info, CheckCircle, Filter, Search, Download, X, Sparkles, Loader } from 'lucide-react'
import { scansApi } from '../lib/api'
import { VulnerabilityModal } from '../components/VulnerabilityModal'
import { CopyButton } from '../components/CopyButton'
import Terminal from '../components/Terminal'
import { useToast } from '../contexts/ToastContext'
import { downloadFile, exportToCSV, exportScanSummaryToCSV, exportToHTML } from '../lib/utils'

function SecurityResults() {
  const { scanId } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const [scan, setScan] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filterSeverity, setFilterSeverity] = useState('ALL')
  const [filterTool, setFilterTool] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedVulnerability, setSelectedVulnerability] = useState(null)
  const [aiSuggestions, setAiSuggestions] = useState(null)
  const [loadingAI, setLoadingAI] = useState(false)
  const [showAIModal, setShowAIModal] = useState(false)

  useEffect(() => {
    loadScanResults()
  }, [scanId])

  // Separate effect for polling - only runs when scan is RUNNING or PENDING
  useEffect(() => {
    if (!scan || scan.status === 'COMPLETED' || scan.status === 'FAILED') {
      return // Don't poll if scan is done
    }
    
    // Poll every 2 seconds for more responsive terminal updates
    const interval = setInterval(loadScanResults, 2000)
    return () => clearInterval(interval)
  }, [scanId, scan?.status])

  const loadScanResults = async () => {
    try {
      const response = await scansApi.getById(scanId)
      setScan(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to load scan results:', error)
      toast.error('Failed to load scan results')
      setLoading(false)
    }
  }

  // Memoize filtered vulnerabilities to avoid re-filtering on every render
  const filteredVulnerabilities = useMemo(() => {
    if (!scan?.vulnerabilities) return []
    
    return scan.vulnerabilities.filter(vuln => {
      const severityMatch = filterSeverity === 'ALL' || vuln.severity === filterSeverity
      const toolMatch = filterTool === 'ALL' || vuln.tool === filterTool
      const searchMatch = searchQuery === '' || 
        vuln.vulnerability_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        vuln.file_path.toLowerCase().includes(searchQuery.toLowerCase()) ||
        vuln.description.toLowerCase().includes(searchQuery.toLowerCase())
      return severityMatch && toolMatch && searchMatch
    })
  }, [scan?.vulnerabilities, filterSeverity, filterTool, searchQuery])

  const clearFilters = () => {
    setFilterSeverity('ALL')
    setFilterTool('ALL')
    setSearchQuery('')
    toast.info('Filters cleared')
  }

  const getAISuggestions = async () => {
    // If scan already has AI suggestions, load them directly
    if (scan.ai_suggestions) {
      setAiSuggestions({
        success: true,
        suggestions: scan.ai_suggestions,
        model: scan.ai_model,
        summary: {
          total_issues: scan.total_issues || 0,
          critical: scan.vulnerabilities?.filter(v => v.severity === 'CRITICAL').length || 0,
          high: scan.vulnerabilities?.filter(v => v.severity === 'HIGH').length || 0,
          medium: scan.vulnerabilities?.filter(v => v.severity === 'MEDIUM').length || 0,
          low: scan.vulnerabilities?.filter(v => v.severity === 'LOW').length || 0
        },
        cached: true,
        generated_at: scan.ai_generated_at
      })
      setShowAIModal(true)
      return
    }

    // Generate new AI suggestions
    setLoadingAI(true)
    try {
      const response = await scansApi.getAISuggestions(scanId)
      setAiSuggestions(response.data)
      setShowAIModal(true)
      
      // Refresh scan data to get saved AI suggestions
      await loadScanResults()
      
      toast.success(response.data.cached ? 'Loaded AI report!' : 'AI analysis complete!')
    } catch (error) {
      console.error('Failed to get AI suggestions:', error)
      toast.error(error.response?.data?.detail || 'Failed to generate AI suggestions')
    } finally {
      setLoadingAI(false)
    }
  }

  const exportResults = (format = 'json') => {
    switch (format) {
      case 'json':
        const data = JSON.stringify({
          scan_id: scanId,
          status: scan.status,
          total_issues: scan.total_issues,
          vulnerabilities: filteredVulns
        }, null, 2)
        downloadFile(data, `scan_${scanId}_results.json`, 'application/json')
        break
      case 'csv':
        exportToCSV(filteredVulns, `scan_${scanId}_vulnerabilities.csv`)
        break
      case 'csv-summary':
        exportScanSummaryToCSV(scan, `scan_${scanId}_summary.csv`)
        break
      case 'html':
        exportToHTML(scan, `scan_${scanId}_report.html`)
        break
    }
    toast.success(`Exported as ${format.toUpperCase()}!`)
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'CRITICAL':
      case 'HIGH':
        return <AlertTriangle className="text-red-600" size={20} />
      case 'MEDIUM':
        return <Info className="text-yellow-600" size={20} />
      case 'LOW':
        return <CheckCircle className="text-blue-600" size={20} />
      default:
        return null
    }
  }

  const getSeverityBadgeClass = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return 'badge-critical'
      case 'HIGH':
        return 'badge-high'
      case 'MEDIUM':
        return 'badge-medium'
      case 'LOW':
        return 'badge-low'
      default:
        return 'badge'
    }
  }

  if (loading && !scan) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-600 border-t-transparent"></div>
      </div>
    )
  }

  if (!scan) {
    return (
      <div className="card text-center">
        <p className="text-gray-600">Scan not found</p>
      </div>
    )
  }

  const filteredVulns = filteredVulnerabilities
  const severityCounts = {
    CRITICAL: scan.vulnerabilities?.filter(v => v.severity === 'CRITICAL').length || 0,
    HIGH: scan.vulnerabilities?.filter(v => v.severity === 'HIGH').length || 0,
    MEDIUM: scan.vulnerabilities?.filter(v => v.severity === 'MEDIUM').length || 0,
    LOW: scan.vulnerabilities?.filter(v => v.severity === 'LOW').length || 0,
  }

  return (
    <div>
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft size={20} />
        Back to Dashboard
      </button>

      {/* Scan Header */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Scan Results #{scanId}</h1>
            <p className="text-gray-600 mt-1">
              Started: {new Date(scan.started_at).toLocaleString()}
            </p>
          </div>
          
          <div className="text-right">
            <span className={`inline-block px-4 py-2 rounded-lg font-semibold ${
              scan.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
              scan.status === 'RUNNING' ? 'bg-blue-100 text-blue-800' :
              scan.status === 'FAILED' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {scan.status}
            </span>
          </div>
        </div>

        {scan.status === 'RUNNING' && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
              <p className="text-blue-800 dark:text-blue-300">Scan in progress... This page will auto-refresh.</p>
            </div>
          </div>
        )}

        {/* Live Progress Terminal */}
        {(scan.status === 'RUNNING' || scan.status === 'PENDING' || scan.progress_log) && (
          <div className="mb-4">
            <Terminal 
              logs={scan.progress_log || ''} 
              title="Live Scan Progress" 
              isRunning={scan.status === 'RUNNING' || scan.status === 'PENDING'}
            />
          </div>
        )}

        {scan.status === 'COMPLETED' && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Total Issues</p>
              <p className="text-3xl font-bold text-gray-900">{scan.total_issues}</p>
            </div>
            
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Critical</p>
              <p className="text-3xl font-bold text-red-600">{severityCounts.CRITICAL}</p>
            </div>
            
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">High</p>
              <p className="text-3xl font-bold text-orange-600">{severityCounts.HIGH}</p>
            </div>
            
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Medium</p>
              <p className="text-3xl font-bold text-yellow-600">{severityCounts.MEDIUM}</p>
            </div>
            
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Low</p>
              <p className="text-3xl font-bold text-blue-600">{severityCounts.LOW}</p>
            </div>
          </div>
        )}

        {scan.health_score !== null && scan.status === 'COMPLETED' && (
          <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Health Score</span>
              <span className={`text-2xl font-bold ${
                scan.health_score >= 80 ? 'text-green-600' :
                scan.health_score >= 60 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {scan.health_score.toFixed(0)}/100
              </span>
            </div>
            <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${
                  scan.health_score >= 80 ? 'bg-green-600' :
                  scan.health_score >= 60 ? 'bg-yellow-600' :
                  'bg-red-600'
                }`}
                style={{ width: `${scan.health_score}%` }}
              />
            </div>
          </div>
        )}

        {/* AI Suggestions Button */}
        {scan.status === 'COMPLETED' && scan.vulnerabilities && scan.vulnerabilities.length > 0 && (
          <div className="mt-4">
            <button
              onClick={getAISuggestions}
              disabled={loadingAI}
              className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-purple-600 via-purple-700 to-indigo-700 dark:from-purple-500 dark:via-purple-600 dark:to-indigo-600 text-white rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl hover:from-purple-700 hover:via-purple-800 hover:to-indigo-800 transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {loadingAI ? (
                <>
                  <Loader className="animate-spin" size={24} />
                  <span>Analyzing vulnerabilities with AI...</span>
                </>
              ) : scan.ai_suggestions ? (
                <>
                  <div className="flex items-center gap-2">
                    <Sparkles size={24} />
                    <span>AI Scan Report</span>
                  </div>
                  <span className="text-xs bg-green-500/30 backdrop-blur px-3 py-1 rounded-full font-medium flex items-center gap-1">
                    <CheckCircle size={14} />
                    <span>Saved</span>
                  </span>
                </>
              ) : (
                <>
                  <div className="flex items-center gap-2">
                    <Sparkles size={24} className="animate-pulse" />
                    <span>AI Suggestions</span>
                  </div>
                  <span className="text-xs bg-white/20 backdrop-blur px-3 py-1 rounded-full font-medium">
                    ✨ Powered by AI
                  </span>
                </>
              )}
            </button>
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-2">
              {scan.ai_suggestions 
                ? `AI report generated ${new Date(scan.ai_generated_at).toLocaleDateString()}`
                : 'Get instant AI-powered recommendations to fix your security issues'
              }
            </p>
          </div>
        )}
      </div>

      {/* Filters */}
      {scan.status === 'COMPLETED' && scan.vulnerabilities && scan.vulnerabilities.length > 0 && (
        <>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Filter size={20} className="text-purple-600" />
                <h3 className="font-bold text-gray-900">Filters</h3>
              </div>
              <div className="flex items-center gap-2">
                <div className="relative group">
                  <button
                    className="flex items-center gap-2 px-3 py-1.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                  >
                    <Download size={16} />
                    Export
                  </button>
                  <div className="hidden group-hover:block absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
                    <button
                      onClick={() => exportResults('json')}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      📄 Export as JSON
                    </button>
                    <button
                      onClick={() => exportResults('csv')}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      📊 Export as CSV
                    </button>
                    <button
                      onClick={() => exportResults('csv-summary')}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      📋 Export Summary CSV
                    </button>
                    <button
                      onClick={() => exportResults('html')}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      🌐 Export as HTML
                    </button>
                  </div>
                </div>
                <button
                  onClick={clearFilters}
                  className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
                >
                  <X size={16} />
                  Clear
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search vulnerabilities..."
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Severity</label>
                <select
                  value={filterSeverity}
                  onChange={(e) => setFilterSeverity(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="ALL">All Severities</option>
                  <option value="CRITICAL">Critical ({severityCounts.CRITICAL})</option>
                  <option value="HIGH">High ({severityCounts.HIGH})</option>
                  <option value="MEDIUM">Medium ({severityCounts.MEDIUM})</option>
                  <option value="LOW">Low ({severityCounts.LOW})</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Scanner Tool</label>
                <select
                  value={filterTool}
                  onChange={(e) => setFilterTool(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="ALL">All Tools</option>
                  <option value="bandit">Bandit</option>
                  <option value="safety">Safety</option>
                  <option value="semgrep">Semgrep</option>
                </select>
              </div>
            </div>
            
            <div className="mt-3 flex items-center justify-between text-sm">
              <span className="text-gray-600">
                Showing <span className="font-bold text-purple-600">{filteredVulns.length}</span> of <span className="font-bold">{scan.vulnerabilities.length}</span> issues
              </span>
              {(filterSeverity !== 'ALL' || filterTool !== 'ALL' || searchQuery !== '') && (
                <span className="text-purple-600 font-medium">Filters active</span>
              )}
            </div>
          </div>

          {/* Vulnerabilities List */}
          <div className="space-y-4">
            {filteredVulns.map(vuln => {
              const isCriticalOrHigh = vuln.severity === 'CRITICAL' || vuln.severity === 'HIGH'
              const isLow = vuln.severity === 'LOW'
              
              return (
                <div 
                  key={vuln.id} 
                  className={`card hover:shadow-lg transition cursor-pointer ${
                    vuln.severity === 'CRITICAL' ? 'border-l-4 border-red-600' :
                    vuln.severity === 'HIGH' ? 'border-l-4 border-orange-600' :
                    vuln.severity === 'MEDIUM' ? 'border-l-4 border-yellow-600' :
                    'border-l-4 border-blue-400'
                  }`}
                  onClick={() => setSelectedVulnerability(vuln)}
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      {getSeverityIcon(vuln.severity)}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <h3 className="font-bold text-lg text-gray-900 hover:text-purple-600 transition-colors">
                            {vuln.vulnerability_type}
                          </h3>
                          <div className="flex items-center gap-2 mt-1">
                            <p className="text-sm text-gray-600">
                              {vuln.file_path}
                              {vuln.line_number && `:${vuln.line_number}`}
                            </p>
                            <CopyButton text={vuln.file_path} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                        </div>
                        
                        <div className="flex gap-2">
                          <span className={`badge ${getSeverityBadgeClass(vuln.severity)}`}>
                            {vuln.severity}
                          </span>
                          <span className="badge bg-gray-100 text-gray-700">
                            {vuln.tool}
                          </span>
                        </div>
                      </div>

                      {/* Show full description for CRITICAL/HIGH */}
                      {isCriticalOrHigh && (
                        <>
                          <p className="text-gray-700 mb-3">{vuln.description}</p>
                          
                          {vuln.code_snippet && (
                            <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-3">
                              <pre className="text-sm">{vuln.code_snippet}</pre>
                            </div>
                          )}
                          
                          {vuln.cwe_id && (
                            <p className="text-xs text-gray-500">CWE: {vuln.cwe_id}</p>
                          )}
                        </>
                      )}

                      {/* Show truncated description for MEDIUM */}
                      {vuln.severity === 'MEDIUM' && (
                        <>
                          <p className="text-gray-700 mb-2">
                            {vuln.description.length > 150 
                              ? vuln.description.substring(0, 150) + '...' 
                              : vuln.description}
                          </p>
                          {vuln.cwe_id && (
                            <p className="text-xs text-gray-500">CWE: {vuln.cwe_id}</p>
                          )}
                        </>
                      )}

                      {/* Minimal detail for LOW */}
                      {isLow && (
                        <p className="text-sm text-gray-600 italic">
                          Click to view details
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </>
      )}

      {scan.status === 'COMPLETED' && (!scan.vulnerabilities || scan.vulnerabilities.length === 0) && (
        <div className="card text-center py-12">
          <CheckCircle className="mx-auto text-green-600 mb-4" size={64} />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No Issues Found! 🎉</h3>
          <p className="text-gray-600">Your code is looking secure. Keep up the good work!</p>
        </div>
      )}
      
      {/* AI Suggestions Modal */}
      {showAIModal && aiSuggestions && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden animate-slideUp">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-purple-600 via-purple-700 to-indigo-700 dark:from-purple-500 dark:via-purple-600 dark:to-indigo-600 p-6 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/20 rounded-lg backdrop-blur">
                    <Sparkles size={28} className="animate-pulse" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">
                      AI Security Analysis
                      {aiSuggestions.cached && (
                        <span className="ml-3 text-sm font-normal bg-green-500/30 px-2 py-1 rounded">
                          Saved Report
                        </span>
                      )}
                    </h2>
                    <p className="text-purple-100 text-sm mt-1">
                      🤖 Powered by {aiSuggestions.model?.split('/')[1] || aiSuggestions.model}
                      {aiSuggestions.generated_at && (
                        <span className="ml-2 opacity-75">
                          • Generated {new Date(aiSuggestions.generated_at).toLocaleDateString()}
                        </span>
                      )}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowAIModal(false)}
                  className="text-white hover:bg-white/20 p-2 rounded-lg transition-all hover:rotate-90 duration-200"
                  aria-label="Close modal"
                >
                  <X size={24} />
                </button>
              </div>
              
              {/* Summary Stats */}
              <div className="grid grid-cols-4 gap-3 mt-4">
                <div className="bg-white/10 backdrop-blur-md rounded-lg p-3 text-center border border-white/20 hover:bg-white/20 transition">
                  <p className="text-xs text-purple-100 mb-1">Total Issues</p>
                  <p className="text-2xl font-bold">{aiSuggestions.summary.total_issues}</p>
                </div>
                <div className="bg-red-500/20 backdrop-blur-md rounded-lg p-3 text-center border border-red-300/30 hover:bg-red-500/30 transition">
                  <p className="text-xs text-purple-100 mb-1">🔴 Critical</p>
                  <p className="text-2xl font-bold">{aiSuggestions.summary.critical}</p>
                </div>
                <div className="bg-orange-500/20 backdrop-blur-md rounded-lg p-3 text-center border border-orange-300/30 hover:bg-orange-500/30 transition">
                  <p className="text-xs text-purple-100 mb-1">🟠 High</p>
                  <p className="text-2xl font-bold">{aiSuggestions.summary.high}</p>
                </div>
                <div className="bg-yellow-500/20 backdrop-blur-md rounded-lg p-3 text-center border border-yellow-300/30 hover:bg-yellow-500/30 transition">
                  <p className="text-xs text-purple-100 mb-1">🟡 Medium</p>
                  <p className="text-2xl font-bold">{aiSuggestions.summary.medium}</p>
                </div>
              </div>
            </div>
            
            {/* Modal Body */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-280px)] bg-gradient-to-b from-gray-50 to-white dark:from-gray-800 dark:to-gray-900">
              <div className="prose prose-purple dark:prose-invert max-w-none">
                <div className="whitespace-pre-wrap text-gray-800 dark:text-gray-200 leading-relaxed font-normal text-[15px]">
                  {aiSuggestions.suggestions.split('\n').map((line, idx) => {
                    // Bold headers (lines starting with numbers or **text**)
                    if (line.match(/^\d+\.\s\*\*.*\*\*/) || line.match(/^\*\*.*\*\*/)) {
                      return (
                        <p key={idx} className="font-bold text-purple-700 dark:text-purple-400 text-lg mt-4 mb-2">
                          {line.replace(/\*\*/g, '')}
                        </p>
                      )
                    }
                    // Sub-items (lines starting with - or *)
                    if (line.trim().startsWith('-') || line.trim().startsWith('*')) {
                      return (
                        <p key={idx} className="ml-4 text-gray-700 dark:text-gray-300 mb-1">
                          {line}
                        </p>
                      )
                    }
                    // Regular text
                    if (line.trim()) {
                      return (
                        <p key={idx} className="mb-2">
                          {line}
                        </p>
                      )
                    }
                    return <br key={idx} />
                  })}
                </div>
              </div>
              
              {/* Token Usage */}
              {aiSuggestions.usage && (
                <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>✨ Generated using {aiSuggestions.usage.total_tokens || 'N/A'} tokens</span>
                    <span className="text-purple-600 dark:text-purple-400">AI-Powered Analysis</span>
                  </div>
                </div>
              )}
            </div>
            
            {/* Modal Footer */}
            <div className="bg-gray-50 dark:bg-gray-800 p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center gap-3">
              <div className="text-xs text-gray-600 dark:text-gray-400">
                💡 Tip: Save these suggestions for your development team
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    const text = `🔒 AI Security Analysis - ${scan.project?.name || 'ASURA'}\n\nGenerated: ${new Date().toLocaleString()}\nModel: ${aiSuggestions.model}\n\n${aiSuggestions.suggestions}\n\n---\nTotal Issues: ${aiSuggestions.summary.total_issues} | Critical: ${aiSuggestions.summary.critical} | High: ${aiSuggestions.summary.high} | Medium: ${aiSuggestions.summary.medium}`
                    navigator.clipboard.writeText(text)
                    toast.success('Copied to clipboard!')
                  }}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition font-medium"
                >
                  📋 Copy to Clipboard
                </button>
                <button
                  onClick={() => setShowAIModal(false)}
                  className="px-6 py-2 bg-purple-600 dark:bg-purple-500 text-white rounded-lg hover:bg-purple-700 dark:hover:bg-purple-600 transition font-medium shadow-lg"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedVulnerability && (
        <VulnerabilityModal 
          vulnerability={selectedVulnerability}
          onClose={() => setSelectedVulnerability(null)}
        />
      )}
    </div>
  )
}

export default SecurityResults
