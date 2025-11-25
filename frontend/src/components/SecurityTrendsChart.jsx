import { TrendingDown, TrendingUp, Minus } from 'lucide-react'
import { useState, useEffect } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

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
      <div className="bg-dark-800 rounded-xl p-6 border border-white/5 text-center py-12">
        <p className="text-gray-400">Not enough scan data for trends</p>
        <p className="text-sm text-gray-500 mt-2">Run at least 2 scans to see trends</p>
      </div>
    )
  }

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

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-dark-900 border border-white/10 p-3 rounded-lg shadow-xl backdrop-blur-md">
          <p className="text-gray-300 text-sm font-medium mb-2">{label}</p>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center gap-2 text-xs">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
              <span className="text-gray-400 capitalize">{entry.name}:</span>
              <span className="text-white font-mono">{entry.value}</span>
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-dark-800 rounded-xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-white">Security Trends</h3>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-lg ${trend === 'improving' ? 'bg-green-500/10 text-green-500' :
          trend === 'worsening' ? 'bg-red-500/10 text-red-500' :
            'bg-white/5 text-gray-400'
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

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              dy={10}
            />
            <YAxis
              stroke="#6b7280"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="total"
              stroke="#0ea5e9"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorTotal)"
              name="Total Issues"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
