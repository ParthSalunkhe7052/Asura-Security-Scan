import { FileSearch, FolderOpen, Shield, Play } from 'lucide-react'

export function EmptyState({ type = 'scans', onAction, actionLabel }) {
  const states = {
    scans: {
      icon: <FileSearch size={64} className="text-gray-300" />,
      title: 'No Scans Yet',
      description: 'Start your first security scan to discover vulnerabilities in your code.',
      action: 'Start Scan'
    },
    projects: {
      icon: <FolderOpen size={64} className="text-gray-300" />,
      title: 'No Projects',
      description: 'Create your first project to get started with security scanning and code quality analysis.',
      action: 'Create Project'
    },
    vulnerabilities: {
      icon: <Shield size={64} className="text-green-300" />,
      title: 'No Vulnerabilities Found',
      description: 'Great news! Your code looks clean. Keep up the good work!',
      action: null
    },
    metrics: {
      icon: <Shield size={64} className="text-gray-300" />,
      title: 'No Metrics Available',
      description: 'Run a metrics analysis to see code quality insights.',
      action: 'Analyze Code'
    }
  }

  const state = states[type] || states.scans

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
      <div className="mb-6">
        {state.icon}
      </div>
      <h3 className="text-2xl font-bold text-gray-900 mb-2">
        {state.title}
      </h3>
      <p className="text-gray-600 text-center max-w-md mb-6">
        {state.description}
      </p>
      {state.action && onAction && (
        <button
          onClick={onAction}
          className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-all font-semibold shadow-lg hover:shadow-xl"
        >
          <Play size={20} />
          {actionLabel || state.action}
        </button>
      )}
    </div>
  )
}
