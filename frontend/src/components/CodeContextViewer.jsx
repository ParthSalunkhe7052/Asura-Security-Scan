import { useState, useEffect } from 'react'
import { Code, ChevronUp, ChevronDown, Copy, Check } from 'lucide-react'
import { copyToClipboard } from '../lib/utils'

export function CodeContextViewer({ code, lineNumber, linesAround = 5, language = 'python' }) {
  const [copied, setCopied] = useState(false)
  const [expanded, setExpanded] = useState(false)

  const lines = code ? code.split('\n') : []
  const targetLine = lineNumber ? parseInt(lineNumber) : Math.floor(lines.length / 2)
  
  const startLine = expanded ? 1 : Math.max(1, targetLine - linesAround)
  const endLine = expanded ? lines.length : Math.min(lines.length, targetLine + linesAround)
  
  const visibleLines = lines.slice(startLine - 1, endLine)

  const handleCopy = async () => {
    const success = await copyToClipboard(visibleLines.join('\n'))
    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  // Syntax highlighting classes (simple)
  const getLineClass = (lineNum) => {
    if (lineNum === targetLine) {
      return 'bg-red-100 border-l-4 border-red-500'
    }
    return 'hover:bg-gray-50'
  }

  return (
    <div className="bg-gray-900 rounded-xl overflow-hidden shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Code size={16} className="text-gray-400" />
          <span className="text-sm font-medium text-gray-300">
            {language.toUpperCase()} • Line {targetLine}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {lines.length > (linesAround * 2) && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 px-2 py-1 text-xs text-gray-300 hover:bg-gray-700 rounded transition-colors"
            >
              {expanded ? (
                <>
                  <ChevronUp size={14} />
                  Collapse
                </>
              ) : (
                <>
                  <ChevronDown size={14} />
                  Show All ({lines.length} lines)
                </>
              )}
            </button>
          )}
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-1 text-xs text-gray-300 hover:bg-gray-700 rounded transition-colors"
          >
            {copied ? (
              <>
                <Check size={14} className="text-green-400" />
                Copied!
              </>
            ) : (
              <>
                <Copy size={14} />
                Copy
              </>
            )}
          </button>
        </div>
      </div>

      {/* Code Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm font-mono">
          <tbody>
            {visibleLines.map((line, index) => {
              const actualLineNum = startLine + index
              return (
                <tr
                  key={actualLineNum}
                  className={`${getLineClass(actualLineNum)} transition-colors`}
                >
                  {/* Line Number */}
                  <td className="px-4 py-1 text-right text-gray-500 select-none w-16 align-top">
                    {actualLineNum}
                  </td>
                  
                  {/* Code Line */}
                  <td className="px-4 py-1 text-gray-100">
                    <pre className="whitespace-pre-wrap break-all">{line || '\u00A0'}</pre>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Show context indicators */}
      {!expanded && (
        <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-t border-gray-700 text-xs text-gray-400">
          <span>
            {startLine > 1 && `${startLine - 1} lines hidden above`}
          </span>
          <span>
            {endLine < lines.length && `${lines.length - endLine} lines hidden below`}
          </span>
        </div>
      )}
    </div>
  )
}

// Inline compact version
export function CodeSnippet({ code, maxLines = 10 }) {
  const [expanded, setExpanded] = useState(false)
  const lines = code ? code.split('\n') : []
  const visibleLines = expanded ? lines : lines.slice(0, maxLines)
  const hasMore = lines.length > maxLines

  return (
    <div className="bg-gray-900 rounded-lg overflow-hidden">
      <div className="p-4 overflow-x-auto">
        <pre className="text-sm text-gray-100 font-mono">
          <code>{visibleLines.join('\n')}</code>
        </pre>
      </div>
      {hasMore && !expanded && (
        <button
          onClick={() => setExpanded(true)}
          className="w-full px-4 py-2 bg-gray-800 text-gray-300 text-sm hover:bg-gray-700 transition-colors"
        >
          Show {lines.length - maxLines} more lines...
        </button>
      )}
    </div>
  )
}
