import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { copyToClipboard } from '../lib/utils'

export function CopyButton({ text, label, className = '' }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async (e) => {
    e.stopPropagation()
    const success = await copyToClipboard(text)
    
    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <button
      onClick={handleCopy}
      className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-lg transition-all hover:bg-gray-100 text-sm font-medium ${className}`}
      title={`Copy ${label || 'to clipboard'}`}
    >
      {copied ? (
        <>
          <Check className="w-4 h-4 text-green-600" />
          <span className="text-green-600">Copied!</span>
        </>
      ) : (
        <>
          <Copy className="w-4 h-4" />
          {label && <span>{label}</span>}
        </>
      )}
    </button>
  )
}

export function InlineCopyButton({ text, className = '' }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async (e) => {
    e.stopPropagation()
    const success = await copyToClipboard(text)
    
    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <button
      onClick={handleCopy}
      className={`p-1.5 rounded hover:bg-gray-100 transition-colors ${className}`}
      title="Copy"
    >
      {copied ? (
        <Check className="w-4 h-4 text-green-600" />
      ) : (
        <Copy className="w-4 h-4 text-gray-500" />
      )}
    </button>
  )
}
