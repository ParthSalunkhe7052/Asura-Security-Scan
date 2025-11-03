/**
 * Copy text to clipboard with fallback
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} - Success status
 */
export async function copyToClipboard(text) {
  try {
    // Modern clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      return true
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      
      try {
        document.execCommand('copy')
        textArea.remove()
        return true
      } catch (error) {
        console.error('Fallback: Failed to copy', error)
        textArea.remove()
        return false
      }
    }
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    return false
  }
}

/**
 * Format date to relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date) {
  const now = new Date()
  const past = new Date(date)
  const diffInSeconds = Math.floor((now - past) / 1000)

  const intervals = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60,
    second: 1
  }

  for (const [unit, seconds] of Object.entries(intervals)) {
    const interval = Math.floor(diffInSeconds / seconds)
    if (interval >= 1) {
      return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`
    }
  }

  return 'just now'
}

/**
 * Format bytes to human readable size
 */
export function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * Debounce function calls
 */
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Get severity color classes
 */
export function getSeverityColor(severity) {
  const colors = {
    CRITICAL: 'text-red-600 bg-red-50 border-red-200',
    HIGH: 'text-orange-600 bg-orange-50 border-orange-200',
    MEDIUM: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    LOW: 'text-blue-600 bg-blue-50 border-blue-200',
    INFO: 'text-gray-600 bg-gray-50 border-gray-200'
  }
  return colors[severity?.toUpperCase()] || colors.INFO
}

/**
 * Get status color classes
 */
export function getStatusColor(status) {
  const colors = {
    COMPLETED: 'text-green-600 bg-green-50 border-green-200',
    RUNNING: 'text-blue-600 bg-blue-50 border-blue-200',
    PENDING: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    FAILED: 'text-red-600 bg-red-50 border-red-200'
  }
  return colors[status?.toUpperCase()] || colors.PENDING
}

/**
 * Download content as file
 */
export function downloadFile(content, filename, type = 'text/plain') {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * Export vulnerabilities to CSV format
 */
export function exportToCSV(vulnerabilities, filename = 'vulnerabilities.csv') {
  const headers = [
    'ID',
    'Severity',
    'Type',
    'File Path',
    'Line Number',
    'Description',
    'Tool',
    'CWE ID',
    'Confidence'
  ]

  const rows = vulnerabilities.map(v => [
    v.id || '',
    v.severity || '',
    v.vulnerability_type || '',
    v.file_path || '',
    v.line_number || '',
    `"${(v.description || '').replace(/"/g, '""')}"`, // Escape quotes
    v.tool || '',
    v.cwe_id || '',
    v.confidence || ''
  ])

  const csv = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')

  downloadFile(csv, filename, 'text/csv')
}

/**
 * Export scan summary to CSV
 */
export function exportScanSummaryToCSV(scan, filename = 'scan_summary.csv') {
  const data = [
    ['Scan Summary'],
    [''],
    ['Field', 'Value'],
    ['Scan ID', scan.id],
    ['Status', scan.status],
    ['Started At', new Date(scan.started_at).toLocaleString()],
    ['Completed At', scan.completed_at ? new Date(scan.completed_at).toLocaleString() : 'N/A'],
    ['Duration (seconds)', scan.duration_seconds || 'N/A'],
    ['Total Issues', scan.total_issues || 0],
    [''],
    ['Severity Breakdown'],
    ['Critical', scan.vulnerabilities?.filter(v => v.severity === 'CRITICAL').length || 0],
    ['High', scan.vulnerabilities?.filter(v => v.severity === 'HIGH').length || 0],
    ['Medium', scan.vulnerabilities?.filter(v => v.severity === 'MEDIUM').length || 0],
    ['Low', scan.vulnerabilities?.filter(v => v.severity === 'LOW').length || 0]
  ]

  const csv = data.map(row => row.join(',')).join('\n')
  downloadFile(csv, filename, 'text/csv')
}

/**
 * Generate and download HTML report
 */
export function exportToHTML(scan, filename = 'scan_report.html') {
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ASURA Security Scan Report #${scan.id}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; padding: 20px; background: #f5f5f5; }
    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    h1 { color: #7c3aed; border-bottom: 3px solid #7c3aed; padding-bottom: 10px; margin-bottom: 20px; }
    h2 { color: #4c1d95; margin-top: 30px; margin-bottom: 15px; }
    .header-info { background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
    .stat-card { text-align: center; padding: 20px; background: #f9fafb; border-radius: 8px; border: 2px solid #e5e7eb; }
    .stat-value { font-size: 32px; font-weight: bold; }
    .stat-label { font-size: 14px; color: #6b7280; margin-top: 5px; }
    .critical { color: #dc2626; }
    .high { color: #ea580c; }
    .medium { color: #ca8a04; }
    .low { color: #2563eb; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th { background: #7c3aed; color: white; padding: 12px; text-align: left; }
    td { padding: 12px; border-bottom: 1px solid #e5e7eb; }
    tr:hover { background: #f9fafb; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-critical { background: #fee2e2; color: #dc2626; }
    .badge-high { background: #ffedd5; color: #ea580c; }
    .badge-medium { background: #fef3c7; color: #ca8a04; }
    .badge-low { background: #dbeafe; color: #2563eb; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center; color: #6b7280; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🛡️ ASURA Security Scan Report</h1>
    
    <div class="header-info">
      <p><strong>Scan ID:</strong> ${scan.id}</p>
      <p><strong>Status:</strong> ${scan.status}</p>
      <p><strong>Started:</strong> ${new Date(scan.started_at).toLocaleString()}</p>
      <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
    </div>

    <h2>📊 Summary</h2>
    <div class="stats">
      <div class="stat-card">
        <div class="stat-value">${scan.total_issues || 0}</div>
        <div class="stat-label">Total Issues</div>
      </div>
      <div class="stat-card">
        <div class="stat-value critical">${scan.vulnerabilities?.filter(v => v.severity === 'CRITICAL').length || 0}</div>
        <div class="stat-label">Critical</div>
      </div>
      <div class="stat-card">
        <div class="stat-value high">${scan.vulnerabilities?.filter(v => v.severity === 'HIGH').length || 0}</div>
        <div class="stat-label">High</div>
      </div>
      <div class="stat-card">
        <div class="stat-value medium">${scan.vulnerabilities?.filter(v => v.severity === 'MEDIUM').length || 0}</div>
        <div class="stat-label">Medium</div>
      </div>
      <div class="stat-card">
        <div class="stat-value low">${scan.vulnerabilities?.filter(v => v.severity === 'LOW').length || 0}</div>
        <div class="stat-label">Low</div>
      </div>
    </div>

    ${scan.vulnerabilities && scan.vulnerabilities.length > 0 ? `
    <h2>🔒 Vulnerabilities</h2>
    <table>
      <thead>
        <tr>
          <th>Severity</th>
          <th>Type</th>
          <th>File</th>
          <th>Line</th>
          <th>Tool</th>
        </tr>
      </thead>
      <tbody>
        ${scan.vulnerabilities.map(v => `
          <tr>
            <td><span class="badge badge-${v.severity?.toLowerCase()}">${v.severity}</span></td>
            <td>${v.vulnerability_type}</td>
            <td>${v.file_path}</td>
            <td>${v.line_number || '-'}</td>
            <td>${v.tool}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    ` : '<p>No vulnerabilities found.</p>'}

    <div class="footer">
      <p>Generated by ASURA - AI SecureLab</p>
      <p>Security Testing Platform</p>
    </div>
  </div>
</body>
</html>`

  downloadFile(html, filename, 'text/html')
}
