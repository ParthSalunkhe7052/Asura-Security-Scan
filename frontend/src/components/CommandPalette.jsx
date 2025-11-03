import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Shield, BarChart3, FolderOpen, Clock, Play, Moon, Sun, X } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

export function CommandPalette({ projects = [], onStartScan, onViewMetrics }) {
  const [isOpen, setIsOpen] = useState(false)
  const [search, setSearch] = useState('')
  const navigate = useNavigate()
  const { isDark, toggleTheme } = useTheme()
  const inputRef = useRef(null)

  // Keyboard shortcut to open/close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsOpen(prev => !prev)
      } else if (e.key === 'Escape') {
        setIsOpen(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const commands = [
    {
      id: 'dashboard',
      label: 'Go to Dashboard',
      icon: <Shield size={18} />,
      action: () => navigate('/'),
      keywords: ['home', 'dashboard']
    },
    {
      id: 'projects',
      label: 'Go to Projects',
      icon: <FolderOpen size={18} />,
      action: () => navigate('/projects'),
      keywords: ['projects', 'list']
    },
    {
      id: 'history',
      label: 'Go to Scan History',
      icon: <Clock size={18} />,
      action: () => navigate('/history'),
      keywords: ['history', 'scans', 'past']
    },
    {
      id: 'scan',
      label: 'Start New Scan',
      icon: <Play size={18} />,
      action: () => {
        setIsOpen(false)
        onStartScan && onStartScan()
      },
      keywords: ['scan', 'start', 'security']
    },
    {
      id: 'metrics',
      label: 'View Code Metrics',
      icon: <BarChart3 size={18} />,
      action: () => {
        setIsOpen(false)
        onViewMetrics && onViewMetrics()
      },
      keywords: ['metrics', 'code', 'quality']
    },
    {
      id: 'theme',
      label: `Switch to ${isDark ? 'Light' : 'Dark'} Mode`,
      icon: isDark ? <Sun size={18} /> : <Moon size={18} />,
      action: toggleTheme,
      keywords: ['theme', 'dark', 'light', 'mode']
    }
  ]

  const filteredCommands = commands.filter(cmd =>
    cmd.label.toLowerCase().includes(search.toLowerCase()) ||
    cmd.keywords.some(k => k.includes(search.toLowerCase()))
  )

  if (!isOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
        onClick={() => setIsOpen(false)}
      />
      
      {/* Command Palette */}
      <div className="fixed top-20 left-1/2 -translate-x-1/2 w-full max-w-2xl z-50 p-4">
        <div className="bg-white rounded-xl shadow-2xl border-2 border-gray-200 overflow-hidden">
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200">
            <Search className="text-gray-400" size={20} />
            <input
              ref={inputRef}
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Type a command or search..."
              className="flex-1 outline-none text-lg"
            />
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <X size={18} />
            </button>
          </div>

          {/* Commands List */}
          <div className="max-h-96 overflow-y-auto">
            {filteredCommands.length > 0 ? (
              <div className="py-2">
                {filteredCommands.map(cmd => (
                  <button
                    key={cmd.id}
                    onClick={() => {
                      cmd.action()
                      setIsOpen(false)
                      setSearch('')
                    }}
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-100 transition-colors text-left"
                  >
                    <div className="text-gray-600">{cmd.icon}</div>
                    <span className="font-medium">{cmd.label}</span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-gray-500">
                No commands found
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center gap-4">
              <kbd className="px-2 py-1 bg-white border border-gray-300 rounded">↑↓</kbd>
              <span>Navigate</span>
            </div>
            <div className="flex items-center gap-4">
              <kbd className="px-2 py-1 bg-white border border-gray-300 rounded">Enter</kbd>
              <span>Select</span>
            </div>
            <div className="flex items-center gap-4">
              <kbd className="px-2 py-1 bg-white border border-gray-300 rounded">Esc</kbd>
              <span>Close</span>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

// Hook to open command palette
export function useCommandPalette() {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsOpen(prev => !prev)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return { isOpen, setIsOpen }
}
