import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, AlertTriangle, Info, CheckCircle, Filter, Search, Download, X, Sparkles, Loader, Terminal as TerminalIcon, ChevronDown, ChevronUp, Code, FileText, Shield } from 'lucide-react'
import { scansApi } from '../lib/api'
import { VulnerabilityModal } from '../components/VulnerabilityModal'
import Terminal from '../components/Terminal'
import { useToast } from '../contexts/ToastContext'
import { downloadFile, exportToCSV, exportScanSummaryToCSV, exportToHTML } from '../lib/utils'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

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
  const [expandedVuln, setExpandedVuln] = useState(null)

  useEffect(() => {
    loadScanResults()
  }, [scanId])

  useEffect(() => {
    if (!scan || scan.status === 'COMPLETED' || scan.status === 'FAILED') return
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
    if (scan.ai_suggestions) {
      setAiSuggestions({
        success: true,
        suggestions: scan.ai_suggestions,
        model: scan.ai_model,
        cached: true
      })
      setShowAIModal(true)
      return
    }

    setLoadingAI(true)
    try {
      const response = await scansApi.getAISuggestions(scanId)
      setAiSuggestions(response.data)
      setShowAIModal(true)
      await loadScanResults()
      toast.success(response.data.cached ? 'Loaded AI report!' : 'AI analysis complete!')
    } catch (error) {
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
          vulnerabilities: filteredVulnerabilities
        }, null, 2)
        downloadFile(data, `scan_${scanId}_results.json`, 'application/json')
        break
      case 'csv':
        exportToCSV(filteredVulnerabilities, `scan_${scanId}_vulnerabilities.csv`)
        break
      case 'html':
        exportToHTML(scan, `scan_${scanId}_report.html`)
        break
    }
    toast.success(`Exported as ${format.toUpperCase()}!`)
  }

  if (loading && !scan) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="w-16 h-16 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
      </div>
    )
  }

  if (!scan) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <AlertTriangle className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Scan Not Found</h2>
        <button onClick={() => navigate('/')} className="text-primary-400 hover:text-primary-300">Back to Dashboard</button>
      </div>
    )
  }

  const severityCounts = {
    CRITICAL: scan.vulnerabilities?.filter(v => v.severity === 'CRITICAL').length || 0,
    HIGH: scan.vulnerabilities?.filter(v => v.severity === 'HIGH').length || 0,
    MEDIUM: scan.vulnerabilities?.filter(v => v.severity === 'MEDIUM').length || 0,
    LOW: scan.vulnerabilities?.filter(v => v.severity === 'LOW').length || 0,
  }

  return (
    <div className="space-y-6 pb-20">
      <motion.button
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors group mb-4"
      >
        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        Back to Dashboard
      </motion.button>

      {/* Header Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-dark-800/50 backdrop-blur-md border border-white/5 rounded-2xl p-6 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 p-6 opacity-5 pointer-events-none">
          <TerminalIcon size={150} />
        </div>

        <div className="relative z-10">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
            <div>
              <div className="flex items-center gap-4 mb-2">
                <h1 className="text-3xl font-bold text-white">Scan Results #{scanId}</h1>
                <span className={clsx(
                  "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border",
                  scan.status === 'COMPLETED' ? "bg-green-500/10 text-green-400 border-green-500/20" :
                    scan.status === 'FAILED' ? "bg-red-500/10 text-red-400 border-red-500/20" :
                      "bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse"
                )}>
                  {scan.status}
                </span>
              </div>
              <p className="text-gray-400 flex items-center gap-2 text-sm font-mono">
                <TerminalIcon size={14} />
                Started: {new Date(scan.started_at).toLocaleString()}
              </p>
            </div>

            {scan.status === 'COMPLETED' && (
              <div className="flex gap-3">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={getAISuggestions}
                  disabled={loadingAI}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-xl font-medium shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40 transition-all"
                >
                  {loadingAI ? <Loader className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                  <span>{scan.ai_suggestions ? 'View AI Report' : 'AI Analysis'}</span>
                </motion.button>

                <div className="relative group">
                  <button className="flex items-center gap-2 px-4 py-2 bg-white/5 text-gray-300 rounded-xl hover:bg-white/10 hover:text-white transition-all border border-white/5">
                    <Download className="w-4 h-4" />
                    <span>Export</span>
                  </button>
                  <div className="hidden group-hover:block absolute right-0 mt-2 w-48 bg-dark-800 border border-white/10 rounded-xl shadow-xl py-2 z-20 animate-fade-in">
                    <button onClick={() => exportResults('json')} className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors">JSON</button>
                    <button onClick={() => exportResults('csv')} className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors">CSV</button>
                    <button onClick={() => exportResults('html')} className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors">HTML Report</button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Live Progress */}
          {(scan.status === 'RUNNING' || scan.status === 'PENDING') && (
            <div className="mb-6">
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 mb-4 flex items-center gap-3 animate-pulse">
                <Loader className="animate-spin text-blue-400" />
                <p className="text-blue-300 font-medium">Scan in progress... Analyzing codebase...</p>
              </div>
              <Terminal
                logs={scan.progress_log || ''}
                title="Live Scan Progress"
                isRunning={true}
              />
            </div>
          )}

          {/* Stats Grid */}
          {scan.status === 'COMPLETED' && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {[
                { label: 'Total Issues', value: scan.total_issues, color: 'text-white', bg: 'bg-white/5', border: 'border-white/5' },
                { label: 'Critical', value: severityCounts.CRITICAL, color: 'text-red-500', bg: 'bg-red-500/10', border: 'border-red-500/20' },
                { label: 'High', value: severityCounts.HIGH, color: 'text-orange-500', bg: 'bg-orange-500/10', border: 'border-orange-500/20' },
                { label: 'Medium', value: severityCounts.MEDIUM, color: 'text-yellow-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' },
                { label: 'Low', value: severityCounts.LOW, color: 'text-blue-500', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className={`p-4 rounded-xl border ${stat.border} ${stat.bg} text-center backdrop-blur-sm`}
                >
                  <p className={`text-[10px] uppercase tracking-wider font-bold opacity-70 mb-1 ${stat.color}`}>{stat.label}</p>
                  <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </motion.div>

      {/* Filters & Content */}
      {scan.status === 'COMPLETED' && scan.vulnerabilities?.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="space-y-6"
        >
          {/* Filters Bar */}
          <div className="flex flex-col md:flex-row gap-4 bg-dark-800/30 p-4 rounded-xl border border-white/5">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search vulnerabilities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-dark-900 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-primary-500 transition-colors"
              />
            </div>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="bg-dark-900 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-500 transition-colors"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
            <select
              value={filterTool}
              onChange={(e) => setFilterTool(e.target.value)}
              className="bg-dark-900 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-500 transition-colors"
            >
              <option value="ALL">All Tools</option>
              <option value="bandit">Bandit</option>
              <option value="safety">Safety</option>
              <option value="semgrep">Semgrep</option>
              <option value="detect-secrets">Secrets</option>
              <option value="npm-audit">NPM Audit</option>
            </select>
            <button
              onClick={clearFilters}
              className="px-4 py-2 bg-white/5 text-gray-300 rounded-lg hover:bg-white/10 hover:text-white transition-colors flex items-center gap-2"
            >
              <X size={16} /> Clear
            </button>
          </div>

          {/* Vulnerabilities List */}
          <div className="space-y-3">
            <AnimatePresence>
              {filteredVulnerabilities.map((vuln, index) => (
                <motion.div
                  key={vuln.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`group bg-dark-800/40 border border-white/5 rounded-xl overflow-hidden hover:border-white/10 transition-all duration-300 ${expandedVuln === vuln.id ? 'bg-dark-800/80 border-white/20 shadow-lg' : ''
                    }`}
                >
                  <div
                    onClick={() => setExpandedVuln(expandedVuln === vuln.id ? null : vuln.id)}
                    className="p-4 cursor-pointer flex items-start gap-4"
                  >
                    <div className={clsx(
                      "w-1.5 h-12 rounded-full shrink-0",
                      vuln.severity === 'CRITICAL' ? "bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]" :
                        vuln.severity === 'HIGH' ? "bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.5)]" :
                          vuln.severity === 'MEDIUM' ? "bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.5)]" :
                            "bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]"
                    )} />

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="font-bold text-white group-hover:text-primary-400 transition-colors truncate">
                          {vuln.vulnerability_type}
                        </h3>
                        <span className={clsx(
                          "text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider border",
                          vuln.severity === 'CRITICAL' ? "bg-red-500/10 text-red-400 border-red-500/20" :
                            vuln.severity === 'HIGH' ? "bg-orange-500/10 text-orange-400 border-orange-500/20" :
                              vuln.severity === 'MEDIUM' ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" :
                                "bg-blue-500/10 text-blue-400 border-blue-500/20"
                        )}>
                          {vuln.severity}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 line-clamp-1 mb-2">{vuln.description}</p>
                      <div className="flex items-center gap-2 text-xs font-mono text-gray-500">
                        <FileText size={12} />
                        <span className="truncate">{vuln.file_path}</span>
                        {vuln.line_number && <span className="text-gray-600">:{vuln.line_number}</span>}
                      </div>
                    </div>

                    <div className="flex flex-col items-end gap-2">
                      <span className="text-[10px] font-mono text-gray-500 bg-white/5 px-2 py-1 rounded border border-white/5">
                        {vuln.tool}
                      </span>
                      {expandedVuln === vuln.id ? <ChevronUp className="text-gray-500" size={16} /> : <ChevronDown className="text-gray-500" size={16} />}
                    </div>
                  </div>

                  <AnimatePresence>
                    {expandedVuln === vuln.id && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="border-t border-white/5 bg-dark-900/30"
                      >
                        <div className="p-4 space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Description</h4>
                              <p className="text-sm text-gray-300 leading-relaxed">{vuln.description}</p>
                            </div>
                            <div>
                              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Location</h4>
                              <div className="bg-dark-900 p-2 rounded border border-white/5 font-mono text-xs text-gray-400 break-all">
                                {vuln.file_path}:{vuln.line_number}
                              </div>
                            </div>
                          </div>

                          {vuln.code_snippet && (
                            <div>
                              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                                <Code size={12} /> Code Snippet
                              </h4>
                              <div className="bg-dark-900 rounded-lg p-4 overflow-x-auto border border-white/5 font-mono text-sm text-gray-300">
                                <pre>{vuln.code_snippet}</pre>
                              </div>
                            </div>
                          )}

                          <div className="flex justify-end pt-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                setSelectedVulnerability(vuln)
                              }}
                              className="px-4 py-2 bg-white/5 text-gray-300 rounded-lg hover:bg-white/10 hover:text-white transition-colors text-sm font-medium flex items-center gap-2"
                            >
                              <Info size={16} /> View Full Details
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {scan.status === 'COMPLETED' && filteredVulnerabilities.length === 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center justify-center py-20 text-center bg-green-500/5 rounded-3xl border border-green-500/20 border-dashed"
        >
          <div className="w-24 h-24 rounded-full bg-green-500/10 flex items-center justify-center mb-6 border border-green-500/20 shadow-[0_0_20px_rgba(34,197,94,0.2)]">
            <CheckCircle className="w-12 h-12 text-green-500" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-2">System Secure</h3>
          <p className="text-gray-400 max-w-md">
            No vulnerabilities detected matching your filters. Your code passed all security checks.
          </p>
        </motion.div>
      )}

      {/* AI Modal */}
      <AnimatePresence>
        {showAIModal && aiSuggestions && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/80 backdrop-blur-sm"
              onClick={() => setShowAIModal(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-4xl max-h-[90vh] bg-dark-800 border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
            >
              <div className="p-6 border-b border-white/10 bg-gradient-to-r from-purple-900/50 to-dark-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Sparkles className="text-purple-400 animate-pulse" />
                  <h2 className="text-xl font-bold text-white">AI Security Analysis</h2>
                </div>
                <button onClick={() => setShowAIModal(false)} className="text-gray-400 hover:text-white transition-colors">
                  <X size={24} />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                <div className="prose prose-invert prose-blue max-w-none prose-headings:font-bold prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-p:text-gray-300 prose-li:text-gray-300 prose-code:text-primary-400 prose-code:bg-primary-500/10 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-dark-900 prose-pre:border prose-pre:border-white/10">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h2: ({ node, children, ...props }) => {
                        const text = children?.toString() || '';
                        const isAutoFixPrompt = text.includes('AI AUTO FIX PROMPT') || text.includes('🤖');

                        if (isAutoFixPrompt) {
                          // Extract the prompt content (everything after this heading)
                          const fullText = aiSuggestions.suggestions;
                          const promptStart = fullText.indexOf('## 🤖 AI AUTO FIX PROMPT');
                          const promptContent = promptStart !== -1 ? fullText.substring(promptStart) : '';

                          const [copied, setCopied] = useState(false);

                          const handleCopy = async () => {
                            try {
                              // Extract just the prompt part (remove the heading and format for AI IDE)
                              const lines = promptContent.split('\n');
                              const promptLines = lines.slice(2).filter(line => line.trim() !== '---'); // Skip heading and separator
                              const cleanPrompt = promptLines.join('\n').trim();

                              await navigator.clipboard.writeText(cleanPrompt);
                              setCopied(true);
                              setTimeout(() => setCopied(false), 2000);
                              toast.success('AI Auto Fix Prompt copied to clipboard!');
                            } catch (err) {
                              toast.error('Failed to copy prompt');
                            }
                          };

                          return (
                            <div className="mt-8 mb-4">
                              <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border-2 border-purple-500/30 rounded-xl p-4">
                                <div className="flex items-center justify-between mb-2">
                                  <h2 className="text-xl font-bold flex items-center gap-2 m-0" {...props}>
                                    {children}
                                  </h2>
                                  <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={handleCopy}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${copied
                                        ? 'bg-green-500/20 text-green-400 border-2 border-green-500/50'
                                        : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white border-2 border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/30'
                                      }`}
                                  >
                                    {copied ? (
                                      <>
                                        <CheckCircle className="w-4 h-4" />
                                        <span>Copied!</span>
                                      </>
                                    ) : (
                                      <>
                                        <TerminalIcon className="w-4 h-4" />
                                        <span>Copy Prompt</span>
                                      </>
                                    )}
                                  </motion.button>
                                </div>
                                <p className="text-xs text-gray-400 m-0">
                                  Copy this prompt and paste it into your AI IDE (Windsurf, Cursor, Antigravity) to automatically fix all issues
                                </p>
                              </div>
                            </div>
                          );
                        }

                        return <h2 {...props}>{children}</h2>;
                      }
                    }}
                  >
                    {aiSuggestions.suggestions}
                  </ReactMarkdown>
                </div>
              </div>

              <div className="p-4 border-t border-white/10 bg-dark-900/50 flex justify-end">
                <button
                  onClick={() => setShowAIModal(false)}
                  className="px-6 py-2 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-colors font-medium"
                >
                  Close Report
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

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
