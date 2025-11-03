import { useEffect, useRef } from 'react'
import { Terminal as TerminalIcon } from 'lucide-react'

function Terminal({ logs, title = "Scan Progress", isRunning = true }) {
  const terminalRef = useRef(null)
  
  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [logs])
  
  const logLines = logs ? logs.split('\n').filter(line => line.trim()) : []
  
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-slate-600 overflow-hidden">
      {/* Terminal Header */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-700 dark:from-slate-900 dark:to-slate-800 px-4 py-3 flex items-center justify-between border-b border-slate-600">
        <div className="flex items-center gap-2">
          <TerminalIcon size={18} className="text-green-400" />
          <span className="text-white font-semibold text-sm">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
        </div>
      </div>
      
      {/* Terminal Body */}
      <div
        ref={terminalRef}
        className="bg-slate-900 dark:bg-black p-4 font-mono text-sm overflow-y-auto max-h-96 min-h-[200px]"
      >
        {logLines.length === 0 ? (
          <div className="text-gray-500 italic flex items-center gap-2">
            {isRunning ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-green-400 border-t-transparent"></div>
                <span>Initializing scan...</span>
              </>
            ) : (
              <span>No logs available</span>
            )}
          </div>
        ) : (
          logLines.map((line, index) => (
            <div key={index} className="mb-1 flex items-start gap-2">
              <span className="text-gray-600 select-none">{String(index + 1).padStart(2, '0')}</span>
              <span className={`flex-1 ${
                line.includes('✅') ? 'text-green-400' :
                line.includes('🔍') ? 'text-blue-400' :
                line.includes('❌') ? 'text-red-400' :
                line.includes('⚠️') ? 'text-yellow-400' :
                'text-gray-300'
              }`}>
                {line}
              </span>
            </div>
          ))
        )}
        
        {/* Blinking cursor when running */}
        {isRunning && (
          <div className="flex items-center gap-1 mt-2">
            <span className="text-green-400">$</span>
            <span className="inline-block w-2 h-4 bg-green-400 animate-pulse"></span>
          </div>
        )}
      </div>
    </div>
  )
}

export default Terminal
