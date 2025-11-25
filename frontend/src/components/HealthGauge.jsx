import { motion } from 'framer-motion'

export function HealthGauge({ score, size = 200 }) {
    const radius = size / 2 - 20
    const circumference = 2 * Math.PI * radius
    const offset = circumference - (score / 100) * circumference

    const getColor = (s) => {
        if (s >= 90) return '#22c55e' // Green
        if (s >= 70) return '#eab308' // Yellow
        if (s >= 50) return '#f97316' // Orange
        return '#ef4444' // Red
    }

    const color = getColor(score)

    return (
        <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
            {/* Background Circle */}
            <svg className="transform -rotate-90 w-full h-full">
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="#1f2937"
                    strokeWidth="12"
                    fill="transparent"
                />
                {/* Progress Circle */}
                <motion.circle
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset: offset }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke={color}
                    strokeWidth="12"
                    fill="transparent"
                    strokeDasharray={circumference}
                    strokeLinecap="round"
                    className="drop-shadow-[0_0_10px_rgba(0,0,0,0.5)]"
                />
            </svg>

            {/* Inner Content */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <motion.span
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 }}
                    className="text-4xl font-bold text-white font-mono"
                >
                    {score}
                </motion.span>
                <span className="text-xs text-gray-400 uppercase tracking-wider mt-1">Health Score</span>
            </div>

            {/* Glow Effect */}
            <div
                className="absolute inset-0 rounded-full blur-3xl opacity-20 pointer-events-none"
                style={{ background: `radial-gradient(circle, ${color} 0%, transparent 70%)` }}
            />
        </div>
    )
}
