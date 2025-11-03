import { Shield, CheckCircle, AlertTriangle, Clock } from 'lucide-react'

export function ScanProgress({ status, progress = 0, currentTool = '', estimatedTime = null }) {
  const getStatusIcon = () => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="text-green-500" size={24} />
      case 'FAILED':
        return <AlertTriangle className="text-red-500" size={24} />
      case 'RUNNING':
        return <Shield className="text-blue-500 animate-pulse" size={24} />
      default:
        return <Clock className="text-gray-500" size={24} />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-500'
      case 'FAILED':
        return 'bg-red-500'
      case 'RUNNING':
        return 'bg-blue-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'COMPLETED':
        return 'Scan Complete'
      case 'FAILED':
        return 'Scan Failed'
      case 'RUNNING':
        return currentTool ? `Running ${currentTool}...` : 'Scanning...'
      case 'PENDING':
        return 'Pending...'
      default:
        return status
    }
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
      <div className="flex items-center gap-4 mb-4">
        {getStatusIcon()}
        <div className="flex-1">
          <h3 className="font-bold text-gray-900">{getStatusText()}</h3>
          {estimatedTime && status === 'RUNNING' && (
            <p className="text-sm text-gray-600">
              Estimated time remaining: {estimatedTime}
            </p>
          )}
        </div>
        <span className="text-2xl font-bold text-gray-900">{progress}%</span>
      </div>

      {/* Progress Bar */}
      <div className="relative w-full h-3 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`absolute top-0 left-0 h-full ${getStatusColor()} transition-all duration-500 ease-out`}
          style={{ width: `${progress}%` }}
        >
          {status === 'RUNNING' && (
            <div className="absolute inset-0 bg-white/30 animate-pulse"></div>
          )}
        </div>
      </div>

      {/* Tool Progress */}
      {status === 'RUNNING' && (
        <div className="mt-4 grid grid-cols-3 gap-3">
          {['Bandit', 'Safety', 'Semgrep'].map((tool) => (
            <div
              key={tool}
              className={`p-2 rounded-lg text-center text-sm font-medium transition-all ${
                currentTool?.toLowerCase() === tool.toLowerCase()
                  ? 'bg-blue-100 text-blue-700 border-2 border-blue-300'
                  : 'bg-gray-50 text-gray-600'
              }`}
            >
              {tool}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// Compact version for inline use
export function ScanProgressCompact({ status, progress = 0 }) {
  const getStatusColor = () => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-500'
      case 'FAILED':
        return 'bg-red-500'
      case 'RUNNING':
        return 'bg-blue-500'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${getStatusColor()} transition-all duration-500`}
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <span className="text-sm font-medium text-gray-700">{progress}%</span>
    </div>
  )
}
