import { TrendingDown, TrendingUp, Minus } from 'lucide-react'
import { useState, useEffect } from 'react'

export function SecurityTrendsChart({ scans = [] }) {
  const [chartData, setChartData] = useState([])

  useEffect(() => {
    if (scans && scans.length > 0) {
      // Take last 10 scans and sort by date
      const recentScans = scans
        .filter(s => s.status === 'COMPLETED')
        .slice(0, 10)
        .reverse()

      const data = recentScans.map((scan, index) => ({
        id: scan.id,
        date: new Date(scan.started_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        total: scan.total_issues || 0,
        critical: scan.vulnerabilities?.filter(v => v.severity === 'CRITICAL').length || 0,
        high: scan.vulnerabilities?.filter(v => v.severity === 'HIGH').length || 0,
        medium: scan.vulnerabilities?.filter(v => v.severity === 'MEDIUM').length || 0,
        low: scan.vulnerabilities?.filter(v => v.severity === 'LOW').length || 0,
      }))

      setChartData(data)
    }
  }, [scans])

  if (chartData.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 text-center py-12">
        <p className="text-gray-600">Not enough scan data for trends</p>
        <p className="text-sm text-gray-500 mt-2">Run at least 2 scans to see trends</p>
      </div>
    )
  }

  const maxValue = Math.max(...chartData.map(d => d.total), 10)
  const getTrend = () => {
    if (chartData.length < 2) return 'neutral'
    const first = chartData[0].total
    const last = chartData[chartData.length - 1].total
    if (last < first) return 'improving'
    if (last > first) return 'worsening'
    return 'stable'
  }

  const trend = getTrend()
  const trendPercent = chartData.length >= 2
    ? Math.abs(((chartData[chartData.length - 1].total - chartData[0].total) / chartData[0].total) * 100)
    : 0

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-900">Security Trends</h3>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-lg ${
          trend === 'improving' ? 'bg-green-100 text-green-700' :
          trend === 'worsening' ? 'bg-red-100 text-red-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {trend === 'improving' && <TrendingDown size={16} />}
          {trend === 'worsening' && <TrendingUp size={16} />}
          {trend === 'stable' && <Minus size={16} />}
          <span className="text-sm font-medium">
            {trend === 'improving' && `↓ ${trendPercent.toFixed(0)}%`}
            {trend === 'worsening' && `↑ ${trendPercent.toFixed(0)}%`}
            {trend === 'stable' && 'Stable'}
          </span>
        </div>
      </div>

      {/* Chart */}
      <div className="relative h-64">
        <div className="absolute inset-0 flex items-end justify-between gap-2">
          {chartData.map((data, index) => {
            const heightPercent = (data.total / maxValue) * 100
            return (
              <div key={data.id} className="flex-1 flex flex-col items-center gap-2">
                {/* Bar */}
                <div className="w-full flex flex-col-reverse gap-0.5" style={{ height: '200px' }}>
                  {data.critical > 0 && (
                    <div
                      className="w-full bg-red-500 rounded-t transition-all hover:opacity-80"
                      style={{ height: `${(data.critical / maxValue) * 200}px` }}
                      title={`Critical: ${data.critical}`}
                    ></div>
                  )}
                  {data.high > 0 && (
                    <div
                      className="w-full bg-orange-500 transition-all hover:opacity-80"
                      style={{ height: `${(data.high / maxValue) * 200}px` }}
                      title={`High: ${data.high}`}
                    ></div>
                  )}
                  {data.medium > 0 && (
                    <div
                      className="w-full bg-yellow-500 transition-all hover:opacity-80"
                      style={{ height: `${(data.medium / maxValue) * 200}px` }}
                      title={`Medium: ${data.medium}`}
                    ></div>
                  )}
                  {data.low > 0 && (
                    <div
                      className="w-full bg-blue-500 rounded-b transition-all hover:opacity-80"
                      style={{ height: `${(data.low / maxValue) * 200}px` }}
                      title={`Low: ${data.low}`}
                    ></div>
                  )}
                </div>

                {/* Label */}
                <div className="text-center">
                  <p className="text-xs font-medium text-gray-900">{data.total}</p>
                  <p className="text-xs text-gray-500">{data.date}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-4 text-xs">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 bg-red-500 rounded"></div>
          <span className="text-gray-700">Critical</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 bg-orange-500 rounded"></div>
          <span className="text-gray-700">High</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 bg-yellow-500 rounded"></div>
          <span className="text-gray-700">Medium</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 bg-blue-500 rounded"></div>
          <span className="text-gray-700">Low</span>
        </div>
      </div>
    </div>
  )
}
